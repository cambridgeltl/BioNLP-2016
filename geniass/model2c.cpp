// this is a program for converting a model file to a C source
// so that you can integrate the model data into your binary.
// usage)
//   First, convert the model file into a C source by this program.
//     ./a.out < model > modeldata.c
//   then, complile and link.
//   In your main program, use
//     model.load_from_array(me_model_file)
//   instead of 
//     model.load_from_file("model");

#include <cstdio>
#include <string>
#include <iostream>

using namespace std;

int main()
{
  cout << "typedef struct ME_Model_Data" << endl;
  cout << "{" << endl;
  cout << "  char * label;" << endl;
  cout << "  char * feature;" << endl;
  cout << "  double weight;" << endl;
  cout << "} ME_Model_Data;" << endl << endl;

  cout << "ME_Model_Data me_model_data[] = {" << endl;
  
  string line;
  while  (getline(cin, line)) {
    char label[256], feature[256];
    float weight;
    sscanf(line.c_str(), "%s\t%s\t%f", label, feature, &weight);
    string s;
    for (int i = 0;; i++) {
      if (feature[i] == 0) break;
      if (feature[i] == '\\') s.push_back('\\');
      if (feature[i] == '"') s.push_back('\\');
      s.push_back(feature[i]);
    }
    printf("\t\"%s\",\t\"%s\",\t%f,\n", label, s.c_str(), weight);
  }
  printf("\t\"///\",\t\"///\",\t0,\n");

  cout << "};" << endl;
}
