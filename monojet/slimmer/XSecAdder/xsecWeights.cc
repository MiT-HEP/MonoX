#include <iostream>
#include <vector>

#include "TString.h"
#include "TFile.h"
#include "TH1F.h"

#include "TTree.h"
#include "TBranch.h"
#include "TLorentzVector.h"
#include "TClonesArray.h"

void xsecWeights (TString dir, TString filename = "monojet_POWHEG_DMS_NNPDF30_13TeV_Pseudoscalar_500_1.root", Float_t xsec = 3.172) {

  TFile *file = new TFile(dir + filename,"UPDATE");
  TTree *tree = (TTree*) file->FindObjectAny("events");
  TH1F  *allHist = (TH1F*) file->FindObjectAny("htotal");

  if (!tree->GetBranch("XSecWeight") && xsec > 0) {

    Float_t mcWeight = 1.;
    
    TBranch *mcBr = tree->GetBranch("mcWeight");
    std::cout << mcBr << std::endl;
    mcBr->SetAddress(&mcWeight);
    
    Float_t XSecWeight = 1.;
    TBranch *XSecWeightBr = tree->Branch("XSecWeight",&XSecWeight,"XSecWeight/F");
    std::cout << XSecWeightBr << std::endl;

    int numEntries = tree->GetEntriesFast();
    Float_t mostWeight = xsec/allHist->GetBinContent(1) * 1000;
    
    for (int entry = 0; entry < numEntries; entry++) {
      if (entry % 500000 == 0)
        std::cout << "Processing... " << float(entry)/float(numEntries)*100 << "%" << std::endl;
      mcBr->GetEntry(entry);
      XSecWeight =  mostWeight * mcWeight;
      XSecWeightBr->Fill();
    }
  }
  else {
    if (xsec > 0)
      std::cout << filename << " already has the xsec Branch!" << std::endl;
    else
      std::cout << filename << " is data. Don't need the xsec Branch!" << std::endl;
  }

  tree->Write();
  file->Close();
}
