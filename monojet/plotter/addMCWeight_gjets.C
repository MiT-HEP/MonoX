void addMCWeight_gjets(TString filename, TString treename)
{

    using namespace std;

    cout << "GJets adding MCWeight to:"<< filename << endl;

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
        
        double kfactor = (1.24087232993*(genBos_pt>100.0&&genBos_pt<=150.0)+1.55807026252*(genBos_pt>150.0&&genBos_pt<=200.0)+1.51043242876*(genBos_pt>200.0&&genBos_pt<=250.0)+1.47333461572*(genBos_pt>250.0&&genBos_pt<=300.0)+1.43497331471*(genBos_pt>300.0&&genBos_pt<=350.0)+1.37846354687*(genBos_pt>350.0&&genBos_pt<=400.0)+1.2920177717*(genBos_pt>400.0&&genBos_pt<=500.0)+1.31414429236*(genBos_pt>500.0&&genBos_pt<=600.0)+1.20453974747*(genBos_pt>600.0&&genBos_pt<=1000.0));

        double ewk = (0.998568444581*(genBos_pt>100.0&&genBos_pt<=150.0)+0.992098286517*(genBos_pt>150.0&&genBos_pt<=200.0)+0.986010290609*(genBos_pt>200.0&&genBos_pt<=250.0)+0.980265498435*(genBos_pt>250.0&&genBos_pt<=300.0)+0.974830448283*(genBos_pt>300.0&&genBos_pt<=350.0)+0.969676202351*(genBos_pt>350.0&&genBos_pt<=400.0)+0.962417128177*(genBos_pt>400.0&&genBos_pt<=500.0)+0.953511139209*(genBos_pt>500.0&&genBos_pt<=600.0)+0.934331895615*(genBos_pt>600.0&&genBos_pt<=1000.0));
        
        scaleMC_w = scale_w*mcWeight*w_npv*kfactor*ewk;
        branch->Fill();
    }

    file->cd();
    oldtree->CloneTree()->Write(treename, TObject::kOverwrite);
    file->Close();
  
}
