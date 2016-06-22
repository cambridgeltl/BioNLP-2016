#include <iostream>
#include <iomanip>
#include <string>
#include <list>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include "maxent.h"

using namespace std;

void split(string& str, vector<string>& tokens)
{
    istringstream in(str);
    char c;

    while (in){
        string token;
        token = "";
        while (in.get(c) && (c != '\t')) token.push_back(c);
        tokens.push_back(token);
    }
}

int main(int argc, char* argv[])
{
	if (argc < 3 || argc > 4) {
		cerr << "Usage: " << argv[0] << "input output [path-to-ruby]" << endl;
		exit(1);
	}

    ME_Model model;

    string inFile = argv[1];
    string outFile = argv[2];
    //string modelFile = argv[3];
    string modelFile = "model1-1.0";
	string rubyCommand = (argc == 4) ? argv[3] : "ruby";

	string eventFile = inFile + ".event";
	string resultFile = inFile + ".result";

    cerr << "Extracting events.";

	string extractionCommand = 
    	rubyCommand + " EventExtracter.rb " + inFile + " " + eventFile;
    system(extractionCommand.c_str());

    cerr << "roading model file." << endl;
    model.load_from_file(modelFile.c_str());
    //model.load_from_file("model" + setID + "-" + ineq);
    //ifstream fileIn(string("/home/users/y-matsu/private/workspace/eclipse-workspace/GENIASS/" + setID + "/test.txt").c_str());
    //ofstream fileOut(string("/home/users/y-matsu/private/workspace/eclipse-workspace/GENIASS/" + setID + "/test-" + ineq + ".prob").c_str());

    ifstream fileIn(eventFile.c_str());
    ofstream fileOut(resultFile.c_str());

    string line, markedTxt;

    getline(fileIn, markedTxt);
    cerr << "start classification." << endl;
    while (getline(fileIn, line)){
        vector<string> tokens;
        split(line, tokens);
        ME_Sample s;

        for(vector<string>::const_iterator token = tokens.begin() + 1;
				token != tokens.end(); ++token){
            s.add_feature(*token);
        }

        (void) model.classify(s);
        fileOut << s.label << endl;
    }
    fileOut.close();
    fileIn.close();

    remove(eventFile.c_str());

	string splitCommand =
    	rubyCommand + " Classifying2Splitting.rb "
		+ resultFile + " " + markedTxt + " " + outFile;

    system(splitCommand.c_str());

	return 0;
}

