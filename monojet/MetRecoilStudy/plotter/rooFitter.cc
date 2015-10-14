#ifndef __CINT__
#include "RooGlobalFunc.h"
#endif
#include "RooAddModel.h"
#include "RooArgList.h"
#include "RooDataSet.h"
#include "RooRealVar.h"
#include "RooGaussian.h"
#include "RooProdPdf.h"
#include "RooPolyVar.h"
#include "RooFormulaVar.h"
#include "TFile.h"
#include "TTree.h"
using namespace RooFit ;

void rooFitter() {

  // Variables used
  RooRealVar dilep_pt("dilep_pt","dilep_pt",-10,1000);
  RooRealVar u_perpZ("u_perpZ","u_perpZ",-10000,10000);
  RooRealVar u_paraZ("u_paraZ","u_paraZ",-10000,10000);

  RooFormulaVar response("response","(u_paraZ+dilep_pt)",RooArgList(u_paraZ,dilep_pt));

  // Linear function for mean
  RooRealVar mu0("mu0","mu0",0,-50,50);
  RooRealVar mu1("mu1","mu1",0,-1,1);
  RooPolyVar mu("mu","mu",dilep_pt,RooArgSet(mu0,mu1));

  // Quad function for sigma1
  RooRealVar sigma10("sigma10","sigma10",0,-50,50);
  RooRealVar sigma11("sigma11","sigma11",0,-10,10);
  RooRealVar sigma12("sigma12","sigma12",0,-1,1);
  RooPolyVar sigma1("sigma1","sigma1",dilep_pt,RooArgSet(sigma10,sigma11,sigma12));
  
  // Quad function for sigma2
  RooRealVar sigma20("sigma20","sigma20",0,-50,50);
  RooRealVar sigma21("sigma21","sigma21",0,-10,10);
  RooRealVar sigma22("sigma22","sigma22",0,-1,1);
  RooPolyVar sigma2("sigma2","sigma2",dilep_pt,RooArgSet(sigma20,sigma21,sigma22));

  // Quad function for sigma3
  RooRealVar sigma30("sigma30","sigma30",0,-50,50);
  RooRealVar sigma31("sigma31","sigma31",0,-10,10);
  RooRealVar sigma32("sigma32","sigma32",0,-1,1);
  RooPolyVar sigma3("sigma3","sigma3",dilep_pt,RooArgSet(sigma30,sigma31,sigma32));

  // Fractional weight
  RooFormulaVar frac1("frac1","(sigma3 - sigma1)/(sigma2 - sigma1)",RooArgList(sigma1,sigma2,sigma3));
  RooFormulaVar frac2("frac2","(sigma3 - sigma2)/(sigma1 - sigma2)",RooArgList(sigma1,sigma2,sigma3));
  
  // Two Gaussians
  RooGaussian gaus1("gaus1","gaus1",response,mu,sigma1);
  RooGaussian gaus2("gaus2","gaus2",response,mu,sigma2);
  RooAddModel twoGaus("twoGaus","twoGaus",RooArgList(gaus1,gaus2),RooArgList(frac1,frac2));

  TFile *inFile = new TFile("/afs/cern.ch/work/d/dabercro/public/Winter15/flatTrees/monojet_DYJetsToLL_M-50.root");
  TTree *inTree = (TTree*) inFile->Get("events");

  TString cut = "((lep1PdgId*lep2PdgId == -169) && abs(dilep_m - 91) < 15 && n_looselep == 2 && n_tightlep == 2 && n_loosepho == 0 && n_tau == 0 && lep2Pt > 20 && n_bjetsLoose == 0 && jet1isMonoJetId == 1)";

  TFile *tempFile = new TFile("smallTree.root","RECREATE");
  TTree *cutTree = inTree->CopyTree(cut);
  cutTree->Write();

  RooDataSet inData = RooDataSet("dataset","dataset",cutTree,RooArgList(u_perpZ,u_paraZ));

  twoGaus.fitTo(inData,ConditionalObservables(dilep_pt));

  tempFile->Close();
  inFile->Close();

}
