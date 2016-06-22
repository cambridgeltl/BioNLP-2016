/*
 * $Id: maxent.h,v 1.1.1.1 2007/01/25 09:01:39 y-matsu Exp $
 */

#ifndef __MAXENT_H_
#define __MAXENT_H_

#include <string>
#include <vector>
#include <list>
#include <map>
#include <algorithm>
#include <iostream>
#include <string>
#include <cassert>
#include "blmvm.h"

#define USE_HASH_MAP  // if you encounter errors with hash, try commenting out this line. (the program will be a bit slower, though)
#ifdef USE_HASH_MAP
#include <ext/hash_map>
#endif

// the data format of each sample for training/testing
struct ME_Sample
{
public:
  ME_Sample() : label("") {};
  ME_Sample(const std::string & l) : label(l) {};
  void set_label(const std::string & l) { label = l; }
  void add_feature(const std::string & f) {
    features.push_back(f);   // binary features
  }
  void add_feature(const std::pair<std::string, double> & f) {
    rvfeatures.push_back(f); // real-valued features
  }
public:
  std::string label;
  std::vector<std::string> features;
  std::vector<std::pair<std::string, double> > rvfeatures;
};

// for those who want to use load_from_array()
typedef struct ME_Model_Data
{
  char * label;
  char * feature;
  double weight;
} ME_Model_Data;


class ME_Model
{
public:

  void add_training_sample(const ME_Sample & s);
  int train(const int cutoff = 0, const double sigma = 0, const double widthfactor = 0);
  int train(const std::vector<ME_Sample> & train,
            const int cutoff = 0, const double sigma = 0, const double widthfactor = 0);
  std::vector<double> classify(ME_Sample & s) const;
  bool load_from_file(const std::string & filename);
  bool save_to_file(const std::string & filename) const;
  int num_classes() const { return _num_classes; }
  std::string get_class_label(int i) const { return _label_bag.Str(i); }
  int get_class_id(const std::string & s) const { return _label_bag.Id(s); }
  void get_features(std::list< std::pair< std::pair<std::string, std::string>, double> > & fl);
  void set_heldout(const int h, const int n = 0) { _nheldout = h; _early_stopping_n = n; };
  bool load_from_array(const ME_Model_Data data[]);

  ME_Model() {
    _nheldout = 0;
    _early_stopping_n = 0;
  }

private:  
  
  struct Sample {
    int label;
    std::vector<int> positive_features;
    std::vector<std::pair<int, double> > rvfeatures;
  };

  struct ME_Feature
  {
    //    ME_Feature(const int l, const int f) : _body((l << 24) + f) {
    //      assert(l >= 0 && l < 256);
    //      assert(f >= 0 && f <= 0xffffff);
    //    };
    //    int label() const { return _body >> 24; }
    //    int feature() const { return _body & 0xffffff; }
    ME_Feature(const int l, const int f) : _body((f << 8) + l) {
      assert(l >= 0 && l < 256);
      assert(f >= 0 && f <= 0xffffff);
    };
    int label() const { return _body & 0xff; }
    int feature() const { return _body >> 8; }
    unsigned int body() const { return _body; }
  private:
    unsigned int _body;
  };

  struct ME_FeatureBag
  {
#ifdef USE_HASH_MAP
    typedef __gnu_cxx::hash_map<unsigned int, int> map_type;
#else    
    typedef std::map<unsigned int, int> map_type;
#endif
    map_type mef2id;
    std::vector<ME_Feature> id2mef;
    int Put(const ME_Feature & i) {
      map_type::const_iterator j = mef2id.find(i.body());
      if (j == mef2id.end()) {
        int id = id2mef.size();
        id2mef.push_back(i);
        mef2id[i.body()] = id;
        return id;
      }
      return j->second;
    }
    int Id(const ME_Feature & i) const {
      map_type::const_iterator j = mef2id.find(i.body());
      if (j == mef2id.end()) {
        return -1;
      }
      return j->second;
    }
    ME_Feature Feature(int id) const {
      assert(id >= 0 && id < (int)id2mef.size());
      return id2mef[id];
    }
    int Size() const {
      return id2mef.size();
    }
    void Clear() {
      mef2id.clear();
      id2mef.clear();
    }
  };

  struct hashfun_str
  {
    size_t operator()(const std::string& s) const {
      assert(sizeof(int) == 4 && sizeof(char) == 1);
      const int* p = reinterpret_cast<const int*>(s.c_str());
      size_t v = 0;
      int n = s.size() / 4;
      for (int i = 0; i < n; i++, p++) {
        //      v ^= *p;
        v ^= *p << (4 * (i % 2)); // note) 0 <= char < 128
      }
      int m = s.size() % 4;
      for (int i = 0; i < m; i++) {
        v ^= s[4 * n + i] << (i * 8);
      }
      return v;
    }
  };

  struct MiniStringBag
  {
#ifdef USE_HASH_MAP
    typedef __gnu_cxx::hash_map<std::string, int, hashfun_str> map_type;
#else    
    typedef std::map<std::string, int> map_type;
#endif
    int _size;
    map_type str2id;
    MiniStringBag() : _size(0) {}
    int Put(const std::string & i) {
      map_type::const_iterator j = str2id.find(i);
      if (j == str2id.end()) {
        int id = _size;
        _size++;
        str2id[i] = id;
        return id;
      }
      return j->second;
    }
    int Id(const std::string & i) const {
      map_type::const_iterator j = str2id.find(i);
      if (j == str2id.end())  return -1;
      return j->second;
    }
    int Size() const { return _size; }
    void Clear() { str2id.clear(); _size = 0; }
    map_type::const_iterator begin() const { return str2id.begin(); }
    map_type::const_iterator end()   const { return str2id.end(); }
  };

  struct StringBag : public MiniStringBag
  {
    std::vector<std::string> id2str;
    int Put(const std::string & i) {
      map_type::const_iterator j = str2id.find(i);
      if (j == str2id.end()) {
        int id = id2str.size();
        id2str.push_back(i);
        str2id[i] = id;
        return id;
      }
      return j->second;
    }
    std::string Str(const int id) const {
      assert(id >= 0 && id < (int)id2str.size());
      return id2str[id];
    }
    int Size() const { return id2str.size(); }
    void Clear() {
      str2id.clear();
      id2str.clear();
    }
  };

  std::vector<Sample> _vs; // vector of training_samples
  StringBag _label_bag;
  MiniStringBag _featurename_bag;
  double _sigma; // Gaussian prior
  double _inequality_width;
  std::vector<double> _vl;  // vector of lambda
  std::vector<double> _va;  // vector of alpha (for inequality ME)
  std::vector<double> _vb;  // vector of beta  (for inequality ME)
  ME_FeatureBag _fb;
  int _num_classes;
  std::vector<double> _vee;  // empirical expectation
  std::vector<double> _vme;  // empirical expectation
  std::vector< std::vector< int > > _sample2feature;
  std::vector< std::vector< std::pair<int, double> > > _sample2feature_rv;
  //  std::vector< Sample > _train;
  std::vector< int >    _train; // keep the labels of the training samples
  std::vector< Sample > _heldout;
  double _train_error;   // current error rate on the training data
  double _heldout_error; // current error rate on the heldout data
  int _nheldout;
  int _early_stopping_n;
  std::vector<double> _vhlogl;

  double heldout_likelihood();
  void conditional_probability(const Sample & nbs, std::vector<double> & membp) const;
  int make_feature_bag(const int cutoff);
  int classify(const Sample & nbs, std::vector<double> & membp) const;
  double update_model_expectation();
  int perform_LMVM();
  int perform_GIS(int C);

  // BLMVM
  int BLMVMComputeFunctionGradient(BLMVM blmvm, BLMVMVec X,double *f,BLMVMVec G);
  int BLMVMComputeBounds(BLMVM blmvm, BLMVMVec XL, BLMVMVec XU);
  int BLMVMSolve(double *x, int n);
  int BLMVMFunctionGradient(double *x, double *f, double *g, int n);
  int BLMVMLowerAndUpperBounds(double *xl,double *xu,int n);
  int Solve_BLMVM(BLMVM blmvm, BLMVMVec X);
  
};


#endif


/*
 * $Log: maxent.h,v $
 * Revision 1.1.1.1  2007/01/25 09:01:39  y-matsu
 *
 *
 * Revision 1.1.1.1  2006/09/14 10:33:25  y-matsu
 *
 *
 * Revision 1.19  2005/12/23 10:33:02  tsuruoka
 * support real-valued features
 *
 * Revision 1.18  2005/12/23 09:15:29  tsuruoka
 * modify _train to reduce memory consumption
 *
 * Revision 1.17  2005/10/28 13:02:34  tsuruoka
 * set_heldout(): add default value
 * Feature()
 *
 * Revision 1.16  2005/09/12 13:51:16  tsuruoka
 * Sample: list -> vector
 *
 * Revision 1.15  2005/09/12 13:27:10  tsuruoka
 * add add_training_sample()
 *
 * Revision 1.14  2005/04/27 11:22:27  tsuruoka
 * bugfix
 * ME_Sample: list -> vector
 *
 * Revision 1.13  2005/04/27 10:20:19  tsuruoka
 * MiniStringBag -> StringBag
 *
 * Revision 1.12  2005/04/27 10:00:42  tsuruoka
 * remove tmpfb
 *
 * Revision 1.11  2005/04/26 14:25:53  tsuruoka
 * add MiniStringBag, USE_HASH_MAP
 *
 * Revision 1.10  2004/10/04 05:50:25  tsuruoka
 * add Clear()
 *
 * Revision 1.9  2004/08/09 12:27:21  tsuruoka
 * change messages
 *
 * Revision 1.8  2004/08/04 13:55:19  tsuruoka
 * modify _sample2feature
 *
 * Revision 1.7  2004/07/29 05:51:13  tsuruoka
 * remove modeldata.h
 *
 * Revision 1.6  2004/07/28 13:42:58  tsuruoka
 * add AGIS
 *
 * Revision 1.5  2004/07/28 05:54:14  tsuruoka
 * get_class_name() -> get_class_label()
 * ME_Feature: bugfix
 *
 * Revision 1.4  2004/07/27 16:58:47  tsuruoka
 * modify the interface of classify()
 *
 * Revision 1.3  2004/07/26 17:23:46  tsuruoka
 * _sample2feature: list -> vector
 *
 * Revision 1.2  2004/07/26 15:49:23  tsuruoka
 * modify ME_Feature
 *
 * Revision 1.1  2004/07/26 13:10:55  tsuruoka
 * add files
 *
 * Revision 1.18  2004/07/22 08:34:45  tsuruoka
 * modify _sample2feature[]
 *
 * Revision 1.17  2004/07/21 16:33:01  tsuruoka
 * remove some comments
 *
 */
