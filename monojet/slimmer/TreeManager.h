#ifndef _TreeManager_H
#define _TreeManager_H

#include <vector>
#include <map>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <stdio.h>

#include "TObject.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TProfile.h"
#include "TFile.h"
#include "TTree.h"
#include "TVector3.h"
#include "TVector2.h"
#include "TLorentzVector.h"
#include "TObjArray.h"
#include "TClonesArray.h"
//#include <TParameter.h>

using namespace std;

class TreeManager : public TObject {


  TTree* myTree;
  TString dirName;
  TObjArray* Vars;


  std::vector<TString> Names;
  std::vector<double> Doubles;
  std::vector<float> Floats;
  std::vector<int> Ints;
  std::vector<int> Bools;
  std::map<TString,TString> NameVsTypeMap;
  std::map<TString,int> NameVsPosMap;

  public:

  // constructor
  TreeManager(TString Name, TString Title);

  // destructor
  ~TreeManager();

  bool AddVar(TString vName, TString vClass);
  bool AddTClonesArray(TString vName, TString arrType);

  int SetValue( TString vName , double X);

  TObject* ReturnObj(TString vName);
  double ReturnVarValue(TString vName);

  bool InitVars();

  void TreeFill();

  void TreeWrite();

  void TreePrint();

  int findName(TString name);
  
  ClassDef(TreeManager, 1);

 protected:
  
 private:
  
};

#endif
