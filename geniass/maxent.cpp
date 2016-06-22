/*
 * $Id: maxent.cpp,v 1.1.1.1 2007/01/25 09:01:39 y-matsu Exp $
 */

#include "maxent.h"
#include <cmath>
#include <cstdio>

using namespace std;

int
ME_Model::BLMVMFunctionGradient(double *x, double *f, double *g, int n)
{
  const int nf = _fb.Size();

  if (_inequality_width > 0) {
    assert(nf == n/2);
    for (int i = 0; i < nf; i++) {
      _va[i] = x[i];
      _vb[i] = x[i + nf];
      _vl[i] = _va[i] - _vb[i];
    }
  } else {
    assert(nf == n);
    for (int i = 0; i < n; i++) {
      _vl[i] = x[i];
    }
  }
  
  double score = update_model_expectation();

  if (_inequality_width > 0) {
    for (int i = 0; i < nf; i++) {
      g[i]      = -(_vee[i] - _vme[i] - _inequality_width);
      g[i + nf] = -(_vme[i] - _vee[i] - _inequality_width);
    }
  } else {
    if (_sigma == 0) {
      for (int i = 0; i < n; i++) {
        g[i] = -(_vee[i] - _vme[i]);
      }
    } else {
      const double c = 1 / (_sigma * _sigma);
      for (int i = 0; i < n; i++) {
        g[i] = -(_vee[i] - _vme[i] - c * _vl[i]);
      }
    }
  }

  *f = -score;

  return 0;
}

int
ME_Model::BLMVMLowerAndUpperBounds(double *xl,double *xu,int n)
{
  if (_inequality_width > 0) {
    for (int i = 0; i < n; i++){
      xl[i] = 0;
      xu[i] = 10000.0;
    }
    return 0;
  }

  for (int i = 0; i < n; i++){
    xl[i] = -10000.0;
    xu[i] = 10000.0;
  }
  return 0;
}

int
ME_Model::perform_GIS(int C)
{
  cerr << "C = " << C << endl;
  C = 1;
  cerr << "performing AGIS" << endl;
  vector<double> pre_v;
  double pre_logl = -999999;
  for (int iter = 0; iter < 200; iter++) {

    double logl =  update_model_expectation();
    fprintf(stderr, "iter = %2d  C = %d  f = %10.7f  train_err = %7.5f", iter, C, logl, _train_error);
    if (_heldout.size() > 0) {
      double hlogl = heldout_likelihood();
      fprintf(stderr, "  heldout_logl(err) = %f (%6.4f)", hlogl, _heldout_error);
    }
    cerr << endl;

    if (logl < pre_logl) {
      C += 1;
      _vl = pre_v;
      iter--;
      continue;
    }
    if (C > 1 && iter % 10 == 0) C--;

    pre_logl = logl;
    pre_v = _vl;
    for (int i = 0; i < _fb.Size(); i++) {
      double coef = _vee[i] / _vme[i];
      _vl[i] += log(coef) / C;
    }
  }
  cerr << endl;

}

int
ME_Model::perform_LMVM()
{
  cerr << "performing LMVM" << endl;

  if (_inequality_width > 0) {
    int nvars = _fb.Size() * 2;
    double *x = (double*)malloc(nvars*sizeof(double)); 

    // INITIAL POINT
    for (int i = 0; i < nvars / 2; i++) {
      x[i] = _va[i];
      x[i + _fb.Size()] = _vb[i];
    }

    int info = BLMVMSolve(x, nvars);

    for (int i = 0; i < nvars / 2; i++) {
      _va[i] = x[i];
      _vb[i] = x[i + _fb.Size()];
      _vl[i] = _va[i] - _vb[i];
    }
  
    free(x);

    return 0;
  }

  int nvars = _fb.Size();
  double *x = (double*)malloc(nvars*sizeof(double)); 

  // INITIAL POINT
  for (int i = 0; i < nvars; i++) { x[i] = _vl[i]; }

  int info = BLMVMSolve(x, nvars);

  for (int i = 0; i < nvars; i++) { _vl[i] = x[i]; }
  
  free(x);

  return 0;
}

void
ME_Model::conditional_probability(const Sample & nbs,
                                  std::vector<double> & membp) const
{
  int num_classes = membp.size();
  double sum = 0;
  for (int label = 0; label < num_classes; label++) {
    double pow = 0.0;
    for (vector<int>::const_iterator i = nbs.positive_features.begin(); i != nbs.positive_features.end(); i++){
      ME_Feature f(label, *i);
      int id = _fb.Id(f);
      if (id >= 0) {
        pow += _vl[id];
      }
    }
    for (vector<pair<int, double> >::const_iterator i = nbs.rvfeatures.begin(); i != nbs.rvfeatures.end(); i++){
      ME_Feature f(label, i->first);
      int id = _fb.Id(f);
      if (id >= 0) {
        pow += _vl[id] * i->second;
      }
    }
    double prod = exp(pow);
    membp[label] = prod;
    sum += prod;
  }
  for (int label = 0; label < num_classes; label++) {
    membp[label] /= sum;
  }
  
}

int
ME_Model::make_feature_bag(const int cutoff)
{
  int max_label = 0;
  int max_num_features = 0;
  for (std::vector<Sample>::const_iterator i = _vs.begin(); i != _vs.end(); i++) {
    max_label = max(max_label, i->label);
  }
  _num_classes = max_label + 1;

  //  map< int, list<int> > feature2sample;

  // count the occurrences of features
#ifdef USE_HASH_MAP
  typedef __gnu_cxx::hash_map<unsigned int, int> map_type;
#else    
  typedef std::map<unsigned int, int> map_type;
#endif
  map_type count;
  if (cutoff > 0) {
    for (std::vector<Sample>::const_iterator i = _vs.begin(); i != _vs.end(); i++) {
      for (std::vector<int>::const_iterator j = i->positive_features.begin(); j != i->positive_features.end(); j++) {
        count[ME_Feature(i->label, *j).body()]++;
      }
      for (std::vector<pair<int, double> >::const_iterator j = i->rvfeatures.begin(); j != i->rvfeatures.end(); j++) {
        count[ME_Feature(i->label, j->first).body()]++;
      }
    }
  }

  int n = 0; 
  for (std::vector<Sample>::const_iterator i = _vs.begin(); i != _vs.end(); i++, n++) {
    max_num_features = max(max_num_features, (int)(i->positive_features.size()));
    for (std::vector<int>::const_iterator j = i->positive_features.begin(); j != i->positive_features.end(); j++) {
      const ME_Feature feature(i->label, *j);
      if (cutoff > 0 && count[feature.body()] < cutoff) continue;
      int id = _fb.Put(feature);
      //      cout << i->label << "\t" << *j << "\t" << id << endl;
      //      feature2sample[id].push_back(n);
    }
    for (std::vector<pair<int, double> >::const_iterator j = i->rvfeatures.begin(); j != i->rvfeatures.end(); j++) {
      const ME_Feature feature(i->label, j->first);
      if (cutoff > 0 && count[feature.body()] < cutoff) continue;
      int id = _fb.Put(feature);
    }
  }
  count.clear();
  
  //  cerr << "num_classes = " << _num_classes << endl;
  //  cerr << "max_num_features = " << max_num_features << endl;

  int c = 0;
  
  _sample2feature.clear();
  _sample2feature.resize(_vs.size());
  _sample2feature_rv.clear();
  _sample2feature_rv.resize(_vs.size());

  n = 0;
  int n10 = _vs.size() / 10;
  if (n10 == 0) n10 = 1;
  for (std::vector<Sample>::const_iterator i = _vs.begin(); i != _vs.end(); i++) {
    if (n % n10 == 0) cerr << ".";
    for (std::vector<int>::const_iterator j = i->positive_features.begin(); j != i->positive_features.end(); j++){
      for (int k = 0; k < _num_classes; k++) {
        int id = _fb.Id(ME_Feature(k, *j));
        if (id >= 0) {
          _sample2feature[n].push_back(id);
          c++;
        }
      }
    }
    for (std::vector<pair<int, double> >::const_iterator j = i->rvfeatures.begin(); j != i->rvfeatures.end(); j++){
      for (int k = 0; k < _num_classes; k++) {
        int id = _fb.Id(ME_Feature(k, j->first));
        if (id >= 0) {
          _sample2feature_rv[n].push_back(pair<int, double>(id, j->second));
          c++;
        }
      }
    }
    n++;
  }

  //  cerr << "c = " << c << endl;
  
  return max_num_features;
}

double
ME_Model::heldout_likelihood()
{
  double logl = 0;
  int ncorrect = 0;
  for (std::vector<Sample>::const_iterator i = _heldout.begin(); i != _heldout.end(); i++) {
    vector<double> membp(_num_classes);
    int l = classify(*i, membp);
    logl += log(membp[i->label]);
    if (l == i->label) ncorrect++;
  }
  _heldout_error = 1 - (double)ncorrect / _heldout.size();
  
  return logl /= _heldout.size();
}

double
ME_Model::update_model_expectation()
{
  double logl = 0;
  int ncorrect = 0;
  int n = 0;
  vector< vector<double> > membpv;
  for (std::vector<int>::const_iterator i = _train.begin(); i != _train.end(); i++) {
    vector<double> membp(_num_classes);
    int max_label = 0;

    double sum = 0;
    vector<double> powv(_num_classes);
    for (int label = 0; label < _num_classes; label++) powv[label] = 0;
    const vector<int> & fl = _sample2feature[n];
    for (std::vector<int>::const_iterator j = fl.begin(); j != fl.end(); j++){
      powv[_fb.Feature(*j).label()] += _vl[*j];
    }
    const vector<pair<int, double> > & fl2 = _sample2feature_rv[n];
    for (std::vector<pair<int, double> >::const_iterator j = fl2.begin(); j != fl2.end(); j++){
      powv[_fb.Feature(j->first).label()] += _vl[j->first] * j->second;
    }
    std::vector<double>::const_iterator pmax = max_element(powv.begin(), powv.end());
    double offset = max(0.0, *pmax - 700); // to avoid overflow
    for (int label = 0; label < _num_classes; label++) {
      double pow = powv[label] - offset;
      double prod = exp(pow);
      membp[label] = prod;
      sum += prod;
    }
    for (int label = 0; label < _num_classes; label++) {
      membp[label] /= sum;
      if (membp[label] > membp[max_label]) max_label = label;
    }
    
    logl += log(membp[*i]);
    if (max_label == *i) ncorrect++;
    membpv.push_back(membp);
    n++;
  }

  // model expectation
  _vme.resize(_fb.Size());
  for (int i = 0; i < _fb.Size(); i++) {
    _vme[i] = 0;
  }
  for (int n = 0; n < (int)_train.size(); n++) {
    const vector<int> & fl = _sample2feature[n];
    for (vector<int>::const_iterator j = fl.begin(); j != fl.end(); j++) {
      _vme[*j] += membpv[n][_fb.Feature(*j).label()];
    }
    const vector<pair<int, double> > & fl2 = _sample2feature_rv[n];
    for (vector<pair<int, double> >::const_iterator j = fl2.begin(); j != fl2.end(); j++) {
      _vme[j->first] += membpv[n][_fb.Feature(j->first).label()] * j->second;
    }
  }
  for (int i = 0; i < _fb.Size(); i++) {
    _vme[i] /= _train.size();
  }
  
  _train_error = 1 - (double)ncorrect / _train.size();

  logl /= _train.size();
  
  if (_inequality_width > 0) {
    for (int i = 0; i < _fb.Size(); i++) {
      logl -= (_va[i] + _vb[i]) * _inequality_width;
    }
  } else {
    if (_sigma > 0) {
      const double c = 1/(2*_sigma*_sigma);
      for (int i = 0; i < _fb.Size(); i++) {
        logl -= _vl[i] * _vl[i] * c;
      }
    }
  }

  //logl /= _train.size();
  
  //  fprintf(stderr, "iter =%3d  logl = %10.7f  train_acc = %7.5f\n", iter, logl, (double)ncorrect/train.size());
  //  fprintf(stderr, "logl = %10.7f  train_acc = %7.5f\n", logl, (double)ncorrect/_train.size());

  return logl;
}

int
ME_Model::train(const vector<ME_Sample> & vms, const int cutoff,
                const double sigma, const double widthfactor)
{
  // convert ME_Sample to Sample
  //  vector<Sample> vs;
  _vs.clear();
  for (vector<ME_Sample>::const_iterator i = vms.begin(); i != vms.end(); i++) {
    add_training_sample(*i);
  }

  return train(cutoff, sigma, widthfactor);
}

void
ME_Model::add_training_sample(const ME_Sample & mes)
{
  Sample s;
  s.label = _label_bag.Put(mes.label);
  if (s.label > 255) {
    cerr << "error: too many types of labels." << endl;
    exit(1);
  }
  for (vector<string>::const_iterator j = mes.features.begin(); j != mes.features.end(); j++) {
    s.positive_features.push_back(_featurename_bag.Put(*j));
  }
  for (vector<pair<string, double> >::const_iterator j = mes.rvfeatures.begin(); j != mes.rvfeatures.end(); j++) {
    s.rvfeatures.push_back(pair<int, double>(_featurename_bag.Put(j->first), j->second));
  }
  _vs.push_back(s);
}

int
ME_Model::train(const int cutoff,
                const double sigma, const double widthfactor)
{
  if (sigma > 0 && widthfactor > 0) {
    cerr << "warning: Gausian prior and inequality ME cannot be used at the same time." << endl;
  }
  if (_nheldout >= _vs.size()) {
    cerr << "error: too much heldout data. no training data is available." << endl;
    return 0;
  }
  
  for (int i = 0; i < _nheldout; i++) {
    _heldout.push_back(_vs.back());
    _vs.pop_back();
  }
  for (vector<Sample>::const_iterator i = _vs.begin(); i != _vs.end(); i++) {
    _train.push_back(i->label);
  }
  
  //  _sigma = sqrt(Nsigma2 / (double)_train.size());
  _sigma = sigma;
  _inequality_width = widthfactor / _train.size();
  
  if (cutoff > 0)
    cerr << "cutoff threshold = " << cutoff << endl;
  if (_sigma > 0)
    cerr << "Gaussian prior sigma = " << _sigma << endl;
    //    cerr << "N*sigma^2 = " << Nsigma2 << " sigma = " << _sigma << endl;
  if (widthfactor > 0)
    cerr << "widthfactor = " << widthfactor << endl;
  cerr << "preparing for estimation";
  int C = make_feature_bag(cutoff);
  _vs.clear();
  cerr << "done" << endl;
  cerr << "number of samples = " << _train.size() << endl;
  cerr << "number of features = " << _fb.Size() << endl;

  cerr << "calculating empirical expectation...";
  _vee.resize(_fb.Size());
  for (int i = 0; i < _fb.Size(); i++) {
    _vee[i] = 0;
  }
  for (int n = 0; n < (int)_train.size(); n++) {
    const vector<int> & fl = _sample2feature[n];
    for (vector<int>::const_iterator j = fl.begin(); j != fl.end(); j++) {
      if (_fb.Feature(*j).label() == _train[n]) {
        _vee[*j] += 1.0;
      }
    }
    const vector<pair<int, double> > & fl2 = _sample2feature_rv[n];
    for (vector<pair<int, double> >::const_iterator j = fl2.begin(); j != fl2.end(); j++) {
      if (_fb.Feature(j->first).label() == _train[n]) {
        _vee[j->first] += j->second;
      }
    }
  }
  for (int i = 0; i < _fb.Size(); i++) {
    _vee[i] /= _train.size();
  }
  cerr << "done" << endl;
  
  _vl.resize(_fb.Size());
  for (int i = 0; i < _fb.Size(); i++) _vl[i] = 0.0;
  if (_inequality_width > 0) {
    _va.resize(_fb.Size());
    _vb.resize(_fb.Size());
    for (int i = 0; i < _fb.Size(); i++) {
      _va[i] = 0.0;
      _vb[i] = 0.0;
    }
  }

  //perform_GIS(C);
  perform_LMVM();

  if (_inequality_width > 0) {
    int sum = 0;
    for (int i = 0; i < _fb.Size(); i++) {
      if (_vl[i] != 0) sum++;
    }
    cerr << "number of active features = " << sum << endl;
  }
  
}

void
ME_Model::get_features(list< pair< pair<string, string>, double> > & fl)
{
  fl.clear();
  //  for (int i = 0; i < _fb.Size(); i++) {
  //    ME_Feature f = _fb.Feature(i);
  //    fl.push_back( make_pair(make_pair(_label_bag.Str(f.label()), _featurename_bag.Str(f.feature())), _vl[i]));
  //  }
  for (MiniStringBag::map_type::const_iterator i = _featurename_bag.begin();
       i != _featurename_bag.end(); i++) {
    for (int j = 0; j < _label_bag.Size(); j++) {
      string label = _label_bag.Str(j);
      string history = i->first;
      int id = _fb.Id(ME_Feature(j, i->second));
      if (id < 0) continue;
      fl.push_back( make_pair(make_pair(label, history), _vl[id]) );
    }
  }
}

bool
ME_Model::load_from_file(const string & filename)
{
  FILE * fp = fopen(filename.c_str(), "r");
  if (!fp) {
    cerr << "error: cannot open " << filename << "!" << endl;
    return false;
  }

  _vl.clear();
  _label_bag.Clear();
  _featurename_bag.Clear();
  _fb.Clear();
  char buf[1024];
  while(fgets(buf, 1024, fp)) {
    string line(buf);
    string::size_type t1 = line.find_first_of('\t');
    string::size_type t2 = line.find_last_of('\t');
    string classname = line.substr(0, t1);
    string featurename = line.substr(t1 + 1, t2 - (t1 + 1) );
    float lambda;
    string w = line.substr(t2+1);
    sscanf(w.c_str(), "%f", &lambda);
      
    int label = _label_bag.Put(classname);
    int feature = _featurename_bag.Put(featurename);
    _fb.Put(ME_Feature(label, feature));
    _vl.push_back(lambda);
  }
    
  _num_classes = _label_bag.Size();

  fclose(fp);

  return true;
}

bool
ME_Model::load_from_array(const ME_Model_Data data[])
{
  _vl.clear();
  for (int i = 0;; i++) {
    if (string(data[i].label) == "///") break;
    int label = _label_bag.Put(data[i].label);
    int feature = _featurename_bag.Put(data[i].feature);
    _fb.Put(ME_Feature(label, feature));
    _vl.push_back(data[i].weight);
  }
  _num_classes = _label_bag.Size();
  return true;
}

bool
ME_Model::save_to_file(const string & filename) const
{
  FILE * fp = fopen(filename.c_str(), "w");
  if (!fp) {
    cerr << "error: cannot open " << filename << "!" << endl;
    return false;
  }

  //  for (int i = 0; i < _fb.Size(); i++) {
  //    if (_vl[i] == 0) continue; // ignore zero-weight features
  //    ME_Feature f = _fb.Feature(i);
  //    fprintf(fp, "%s\t%s\t%f\n", _label_bag.Str(f.label()).c_str(), _featurename_bag.Str(f.feature()).c_str(), _vl[i]);
  //  }
  for (MiniStringBag::map_type::const_iterator i = _featurename_bag.begin();
       i != _featurename_bag.end(); i++) {
    for (int j = 0; j < _label_bag.Size(); j++) {
      string label = _label_bag.Str(j);
      string history = i->first;
      int id = _fb.Id(ME_Feature(j, i->second));
      if (id < 0) continue;
      if (_vl[id] == 0) continue; // ignore zero-weight features
      fprintf(fp, "%s\t%s\t%f\n", label.c_str(), history.c_str(), _vl[id]);
    }
  }

  fclose(fp);

  return true;
}

int
ME_Model::classify(const Sample & nbs, vector<double> & membp) const
{
  //  vector<double> membp(_num_classes);
  assert(_num_classes == (int)membp.size());
  conditional_probability(nbs, membp);
  int max_label = 0;
  double max = 0.0;
  for (int i = 0; i < (int)membp.size(); i++) {
    //    cout << membp[i] << " ";
    if (membp[i] > max) { max_label = i; max = membp[i]; }
  }
  //  cout << endl;
  return max_label;
}

vector<double>
ME_Model::classify(ME_Sample & mes) const
{
  Sample s;
  for (vector<string>::const_iterator j = mes.features.begin(); j != mes.features.end(); j++) {
    int id = _featurename_bag.Id(*j);
    if (id >= 0)
      s.positive_features.push_back(id);
  }
  for (vector<pair<string, double> >::const_iterator j = mes.rvfeatures.begin(); j != mes.rvfeatures.end(); j++) {
    int id = _featurename_bag.Id(j->first);
    if (id >= 0) {
      s.rvfeatures.push_back(pair<int, double>(id, j->second));
    }
  }

  vector<double> vp(_num_classes);
  int label = classify(s, vp);
  mes.label = get_class_label(label);
  return vp;
}

/*
 * $Log: maxent.cpp,v $
 * Revision 1.1.1.1  2007/01/25 09:01:39  y-matsu
 *
 *
 * Revision 1.1.1.1  2006/09/14 10:33:25  y-matsu
 *
 *
 * Revision 1.21  2005/12/23 10:33:02  tsuruoka
 * support real-valued features
 *
 * Revision 1.20  2005/12/23 09:15:29  tsuruoka
 * modify _train to reduce memory consumption
 *
 * Revision 1.19  2005/10/28 13:10:14  tsuruoka
 * fix for overflow (thanks to Ming Li)
 *
 * Revision 1.18  2005/10/28 13:03:07  tsuruoka
 * add progress_bar
 *
 * Revision 1.17  2005/09/12 13:51:16  tsuruoka
 * Sample: list -> vector
 *
 * Revision 1.16  2005/09/12 13:27:10  tsuruoka
 * add add_training_sample()
 *
 * Revision 1.15  2005/04/27 11:22:27  tsuruoka
 * bugfix
 * ME_Sample: list -> vector
 *
 * Revision 1.14  2005/04/27 10:00:42  tsuruoka
 * remove tmpfb
 *
 * Revision 1.13  2005/04/26 14:25:53  tsuruoka
 * add MiniStringBag, USE_HASH_MAP
 *
 * Revision 1.12  2005/02/11 10:20:08  tsuruoka
 * modify cutoff
 *
 * Revision 1.11  2004/10/04 05:50:25  tsuruoka
 * add Clear()
 *
 * Revision 1.10  2004/08/26 16:52:26  tsuruoka
 * fix load_from_file()
 *
 * Revision 1.9  2004/08/09 12:27:21  tsuruoka
 * change messages
 *
 * Revision 1.8  2004/08/04 13:55:18  tsuruoka
 * modify _sample2feature
 *
 * Revision 1.7  2004/07/28 13:42:58  tsuruoka
 * add AGIS
 *
 * Revision 1.6  2004/07/28 05:54:13  tsuruoka
 * get_class_name() -> get_class_label()
 * ME_Feature: bugfix
 *
 * Revision 1.5  2004/07/27 16:58:47  tsuruoka
 * modify the interface of classify()
 *
 * Revision 1.4  2004/07/26 17:23:46  tsuruoka
 * _sample2feature: list -> vector
 *
 * Revision 1.3  2004/07/26 15:49:23  tsuruoka
 * modify ME_Feature
 *
 * Revision 1.2  2004/07/26 13:52:18  tsuruoka
 * modify cutoff
 *
 * Revision 1.1  2004/07/26 13:10:55  tsuruoka
 * add files
 *
 * Revision 1.20  2004/07/22 08:34:45  tsuruoka
 * modify _sample2feature[]
 *
 * Revision 1.19  2004/07/21 16:33:01  tsuruoka
 * remove some comments
 *
 */

