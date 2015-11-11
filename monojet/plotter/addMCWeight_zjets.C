void addMCWeight_zjets(TString filename, TString treename)
{

    using namespace std;

    cout << "ZJets adding MCWeight to:"<< filename << endl;

    double scale_w;
    float mcWeight;
    int npv;
    float genBos_pt;

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
    oldtree->SetBranchAddress("genBos_pt",&genBos_pt);

    double scaleMC_w = 1.0;

    TBranch *branch = oldtree->Branch("scaleMC_w",&scaleMC_w,"scaleMC_w/D");

    for(int i = 0; i < oldtree->GetEntries(); i++)
    {
        oldtree->GetEntry(i);
      
        double w_npv = (3.57041 + -1.49846*npv + 0.515829*npv*npv + -0.0839209*npv*npv*npv + 0.00719964*npv*npv*npv*npv + -0.000354548*npv*npv*npv*npv*npv + 1.01544e-05*npv*npv*npv*npv*npv*npv + -1.58019e-07*npv*npv*npv*npv*npv*npv*npv + 1.03663e-09*npv*npv*npv*npv*npv*npv*npv*npv);
        
        double ewk = (0.984525344338*(genBos_pt>100.0&&genBos_pt<=150.0)+0.969078612189*(genBos_pt>150.0&&genBos_pt<=200.0)+0.954626582726*(genBos_pt>200.0&&genBos_pt<=250.0)+0.941059330021*(genBos_pt>250.0&&genBos_pt<=300.0)+0.92828367065*(genBos_pt>300.0&&genBos_pt<=350.0)+0.916219976557*(genBos_pt>350.0&&genBos_pt<=400.0)+0.89931198024*(genBos_pt>400.0&&genBos_pt<=500.0)+0.878692669663*(genBos_pt>500.0&&genBos_pt<=600.0)+0.834717745177*(genBos_pt>600.0&&genBos_pt<=1000.0))
;
        double kfactor = (1.0);
        
        scaleMC_w = scale_w*mcWeight*w_npv*kfactor*ewk;
        branch->Fill();
    }

    file->cd();
    oldtree->CloneTree()->Write(treename, TObject::kOverwrite);
    file->Close();
  
}
