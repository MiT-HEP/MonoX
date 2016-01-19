void addMCWeight(TString filename, TString treename)
{

    using namespace std;

    cout << "adding MCWeight to:"<< filename << endl;

    double scale_w;
    float mcWeight;
    int npv;

    TFile *file = new TFile(filename,"UPDATE");  
    TTree *oldtree = (TTree*)file->Get(treename);

    if(oldtree==NULL)
    {
        cout << "Could not find tree " << treeDir << "/" << treename << endl
             << "in file " << file->GetName() << endl;
        return;
    }
  
    oldtree->SetBranchAddress("scale_w",&scale_w);
    oldtree->SetBranchAddress("mcWeight",&mcWeight);
    oldtree->SetBranchAddress("npv",&npv);

    double scaleMC_w = 1.0;

    TBranch *branch = oldtree->Branch("scaleMC_w",&scaleMC_w,"scaleMC_w/D");

    for(int i = 0; i < oldtree->GetEntries(); i++)
    {
        oldtree->GetEntry(i);
      
        double w_npv = (3.57041 + -1.49846*npv + 0.515829*npv*npv + -0.0839209*npv*npv*npv + 0.00719964*npv*npv*npv*npv + -0.000354548*npv*npv*npv*npv*npv + 1.01544e-05*npv*npv*npv*npv*npv*npv + -1.58019e-07*npv*npv*npv*npv*npv*npv*npv + 1.03663e-09*npv*npv*npv*npv*npv*npv*npv*npv);
        
        scaleMC_w = scale_w*mcWeight*w_npv;
        branch->Fill();
    }

    file->cd();
    oldtree->CloneTree()->Write(treename, TObject::kOverwrite);
    file->Close();
  
}
