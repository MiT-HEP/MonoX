#include "TreeManager.h"

TreeManager::TreeManager(TString Name, TString Title /*, TFile* File*/){
  myTree = new TTree(Name, Title);
  Vars = new TObjArray();
  cout << "Output tree set!" << endl;
}

TreeManager::~TreeManager(){
  delete myTree;
  delete Vars;
}

int TreeManager::findName(TString name){
  if(Names.size() < 1) {
    //     cout << "You haven't added any variables!" << endl;
    return -2;
  }
  for(unsigned int nm = 0; nm < Names.size(); nm++){
    TString test(Names[nm]);
    if(test == name) return nm;
  }
  return -1;
}



bool TreeManager::AddTClonesArray(TString vName, TString arrType){
  if( TreeManager::findName(vName) >= 0 ) {
    cout << "Variable with same name has already been added!" << endl;
    return 0;
  }
  if( TreeManager::findName(vName) == -2) return 0;
  
  TClonesArray* ob = new TClonesArray(arrType, 10000);
  NameVsTypeMap[vName] = "TClonesArray";
  NameVsPosMap[vName] = (int) Vars->GetEntries();
  Vars->Add(ob);
  Names.push_back(vName);
  return 1;
}

TObject* TreeManager::ReturnObj(TString vName){
  int findResult = TreeManager::findName(vName);
  if( findResult == -1 ) {
    cout << "Variable name " << vName << " not found!" << endl;
    return 0;
  }
    if( findResult == -2) {
      cout << "You haven't added any variables yet!" << endl;
      return 0;
    }
    
    TString ObjType( NameVsTypeMap[vName] );
    if( ObjType == "double" || ObjType == "float" || ObjType == "int" || ObjType == "bool"){
	cout << "You used this function with a number, not an object. Please, use ReturnVarValue( TString vName ) instead." << endl;
	return 0;
    }

    int ObjPos = NameVsPosMap[vName];
    return Vars->At(ObjPos);
  }

  double TreeManager::ReturnVarValue(TString vName){
    int findResult = TreeManager::findName(vName);
    if( findResult == -1 ) {
      cout << "Variable name " << vName << " not found!" << endl;
      return -10;
    }
    if( findResult == -2) {
      cout << "You haven't added any variables yet!" << endl;
      return -20;
    }

    TString ObjType( NameVsTypeMap[vName] );
    if( ObjType != "double" && ObjType != "float" && ObjType != "int" && ObjType != "bool"){
	cout << "You used this function with an object, not a number. Please, use ReturnObj( TString vName ) instead." << endl;
	return -30;
    }

    int ObjPos = NameVsPosMap[vName];
    if(ObjType == "double") return Doubles[ObjPos];
    if(ObjType == "float") return (double) Floats[ObjPos];
    if(ObjType == "int") return (double) Ints[ObjPos];
    if(ObjType == "bool") return (double) Bools[ObjPos];
    cout << "Something went wong!" << endl;
    return -40;
  }

  bool TreeManager::AddVar(TString vName, TString vClass){
    cout << "Adding variable " << vName << " of type " << vClass << " to the tree..." << endl;
    if(vClass.Contains("Clones")) {
      cout << "Please use AddTClonesArray(TString vName, TString arrType) method!" << endl;
      return 0;
    }
    int findResult = TreeManager::findName(vName);
    if( findResult >= 0 ) {
      cout << "Variable with same name has already been added!" << endl;
      return 0;
    }
    NameVsTypeMap[vName] = vClass;
    if(vClass.Contains("TVector3") == 1){
       TVector3* ob = new TVector3();
       NameVsPosMap[vName] = (int) Vars->GetEntries();
       Vars->Add(ob);
       Names.push_back(vName);
       return 1;
    }
    if(vClass.Contains("TLorentzVector") == 1){
       TLorentzVector* ob = new TLorentzVector();
       NameVsPosMap[vName] = (int) Vars->GetEntries();
       Vars->Add(ob);
       Names.push_back(vName);
       return 1;
    }
    if(vClass.Contains("TVector2") == 1){
       TVector2* ob = new TVector2();
       NameVsPosMap[vName] = (int) Vars->GetEntries();
       Vars->Add(ob);
       Names.push_back(vName);
       return 1;
    }
    if(vClass.Contains("double") == 1){
      NameVsPosMap[vName] = (int) Doubles.size();
      Doubles.push_back(-10);
      Names.push_back(vName);
      return 1;
    }
    if(vClass.Contains("float") == 1){
      NameVsPosMap[vName] = (int) Floats.size();
      Floats.push_back(-10);
      Names.push_back(vName);
      return 1;
    }
    if(vClass.Contains("int") == 1){
      NameVsPosMap[vName] = (int) Ints.size();
      Ints.push_back(-10);
      Names.push_back(vName);
      return 1;
    }
    if(vClass.Contains("bool") == 1){
      NameVsPosMap[vName] = (int) Bools.size();
      Bools.push_back(0);
      Names.push_back(vName);
      return 1;
    }

    cout << "Variable added. Number of variables added until now: " << Vars->GetEntries() << endl;
    cout << "Class not found - please add it to the macro in the TreeManager.h file!" << endl;
    return 0;
  }

  bool TreeManager::InitVars(){
    cout << "Initializing tree branches..." << endl;

    //if(Vars->GetEntries() == 0){ cout << "WARNING! You haven't added any variables to the tree yet!" << endl; return 0; }

    unsigned int VarsEntries = Vars->GetEntries();
    unsigned int TotalVars = VarsEntries + Doubles.size() + Floats.size() + Ints.size() + Bools.size();
    if( TotalVars != Names.size()){ cout << "Something is wrong, the number of added variables is not matching! Vars: " << TotalVars << " Names: " << Names.size() << endl; return 0; }

    for(unsigned int v = 0; v < Names.size(); v++){

      TString vName( Names[v] );
      TString vClass( NameVsTypeMap[vName] );
      int vPos = NameVsPosMap[vName];

      if(vClass.Contains("TClones") == 1){
        myTree->Branch(vName, vClass, ((TClonesArray*)Vars->At(vPos)));
	cout << "Branch added with variable " << vName << endl;
      }
      if(vClass.Contains("TVector3") == 1){
        myTree->Branch(vName, vClass, ((TVector3*)Vars->At(vPos)));
	cout << "Branch added with variable " << vName << endl;
      }
      if(vClass.Contains("TLorentzVector") == 1){
        myTree->Branch(vName, vClass, ((TLorentzVector*)Vars->At(vPos)));
	cout << "Branch added with variable " << vName << endl;
      }
      if(vClass.Contains("TVector2") == 1){
        myTree->Branch(vName, vClass, ((TVector2*)Vars->At(vPos)));
	cout << "Branch added with variable " << vName << endl;
      }
      if(vClass.Contains("double") == 1){
        TString vType(vName + "/D");
        myTree->Branch(vName, (double *)&( Doubles[vPos] ), vType);
	cout << "Branch added with variable " << vName << endl;
      }
      if(vClass.Contains("float") == 1){
        TString vType(vName + "/F");
        myTree->Branch(vName, (float *)&( Floats[vPos] ), vType);
	cout << "Branch added with variable " << vName << endl;
      }
      if(vClass.Contains("int") == 1){
        TString vType(vName + "/I");
        myTree->Branch(vName, (int *)&( Ints[vPos] ), vType);
	cout << "Branch added with variable " << vName << endl;
      }

      if(vClass.Contains("bool") == 1){
        TString vType(vName + "/O");
        myTree->Branch(vName, (bool *)&( Bools[vPos] ), vType);
      }

    }

    return 1;
  }

  int TreeManager::SetValue( TString vName, double X ){
    int findResult = TreeManager::findName(vName);
    if( findResult == -1 ) {
      cout << "Variable name " << vName << " not found!" << endl;
      return -10;
    }
    if( findResult == -2) {
      cout << "You haven't added any variables yet!" << endl;
      return -20;
    }
    TString ObjType( NameVsTypeMap[vName] );
    if( ObjType != "double" && ObjType != "float" && ObjType != "int" && ObjType != "bool"){
        cout << "You used this function with an object, not a number!" << endl;
        return -30;
    }
    int ObjPos = NameVsPosMap[vName];
    if(ObjType == "double") { Doubles[ObjPos] = (double) X; return 1; }
    if(ObjType == "float") { Floats[ObjPos] = (float) X; return 1; }
    if(ObjType == "int") { Ints[ObjPos] = (int) X; return 1; }
    if(ObjType == "bool") { Bools[ObjPos] = (bool) X; return 1; }
    cout << "Something went wong!" << endl;
    return -40;
}

  void TreeManager::TreeFill(){
    myTree->Fill();

  }


  void TreeManager::TreeWrite(){
//    myFile->cd();
    myTree->Write();
    //myTree->Print();
    cout << "Output tree written with " << myTree->GetEntries() << " entries." <<endl;
  }

 void TreeManager::TreePrint(){
    myTree->Print();
}
