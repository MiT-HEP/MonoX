#include "TreeEntries_simpletree.h"

#include "TTree.h"
#include "TFile.h"
#include "TH1.h"
#include "TLorentzVector.h"
#include "math.h"

void
phi(TTree* _input, char const* _outputName, double _sampleWeight = 1., TH1* _npvweight = 0)
{
  printf("Running skim\n");

  simpletree::Event event;
  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"run", "lumi", "event", "weight", "npv", "photons", "jets", "t1Met"});

  TFile* outputFile(TFile::Open(_outputName, "recreate"));
  TTree* output(new TTree("skim", "efficiency"));

  double weight;

  simpletree::PhotonCollection outTag("tag");
  outTag.init();

  simpletree::PhotonCollection outProbe("probe");
  outProbe.init();

  float probeMass[1];

  bool probeIsPhoton[1];
  float probePtRaw[1];
  float probePtCorrUp[1];
  float probePtCorrDown[1];

  unsigned short njets;

  simpletree::LorentzVectorM recoil;

  float recoilPt;
  float recoilEta;
  float recoilPhi;
  float recoilMass;

  output->Branch("run", &event.run, "run/i");
  output->Branch("lumi", &event.lumi, "lumi/i");
  output->Branch("event", &event.event, "event/i");
  output->Branch("weight", &weight, "weight/D");
  output->Branch("npv", &event.npv, "npv/s");

  outTag.book(*output);
  
  outProbe.book(*output);
  
  output->Branch("probe.mass", probeMass, "probe.mass[probe.size]/F");

  output->Branch("probe.isPhoton", probeIsPhoton, "probe.isPhoton[probe.size]/O");
  output->Branch("probe.ptRaw", probePtRaw, "probe.ptRaw[probe.size]/F");
  output->Branch("probe.ptCorrUp", probePtCorrUp, "probe.ptCorrUp[probe.size]/F");
  output->Branch("probe.ptCorrDown", probePtCorrDown, "probe.ptCorrDown[probe.size]/F");

  output->Branch("njets", &njets, "njets/s");

  output->Branch("recoil.pt", &recoilPt, "recoil.pt/F");
  output->Branch("recoil.eta", &recoilEta, "recoil.eta/F");
  output->Branch("recoil.phi", &recoilPhi, "recoil.phi/F");
  output->Branch("recoil.mass", &recoilMass, "recoil.mass/F");

  output->Branch("t1Met.met", &event.t1Met.met, "t1Met.met/F");
  output->Branch("t1Met.phi", &event.t1Met.phi, "t1Met.phi/F");

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    if (iEntry % 1000000 == 0)
      printf("Event %ld\n", iEntry);
    
    auto& photons(event.photons);
    auto& jets(event.jets);
    auto& t1Met(event.t1Met);
    
    recoil.SetCoordinates(0.,0.,0.,0.);

    unsigned pair[] = {unsigned(-1), unsigned(-1)};

    for (unsigned iTag(0); iTag != photons.size(); ++iTag) {
      auto& tag(photons[iTag]);
      if ( !(tag.medium && tag.pt > 175. && tag.isEB))
	continue;

      // printf("Tag found\n");
      
      for (unsigned iPho(0); iPho != photons.size(); ++iPho) {
	auto& pho(photons[iPho]);
	if ( !(pho.pt > 30. && pho.loose))
	  continue;
	
	// printf("Medium photon found for probe\n");
	  
	if (std::abs(tag.dPhi(pho)) < 2.5)
	  continue;
	
	// printf("tag/probe back to back\n");
	
	outTag.resize(1);
	outTag[0] = tag;

	outProbe.resize(1);

	outProbe[0] = pho;
	probeMass[0] = 0.;

	probeIsPhoton[0] = true;
	probePtRaw[0] = -1.;
	probePtCorrUp[0] = -1.;
	probePtCorrDown[0] = -1.;
	
	pair[0] = iTag;
	pair[1] = iPho;
	break;
      }
      if (pair[0] < photons.size())
	break;

      for (unsigned iJet(0); iJet != jets.size(); ++iJet) {
	auto& jet(jets[iJet]);
	if ( !(jet.pt > 30.))
	  continue;
	
	// printf("Medium photon found for probe\n");
	  
	if (std::abs(tag.dPhi(jet)) < 2.5)
	  continue;
	
	// printf("tag/probe back to back\n");
	
	outTag.resize(1);
	outTag[0] = tag;

	outProbe.resize(1);

	outProbe[0].pt = jet.pt;
	outProbe[0].eta = jet.eta;
	outProbe[0].phi = jet.phi;
	probeMass[0] = jet.mass;

	probeIsPhoton[0] = false;
	probePtRaw[0] = jet.ptRaw;
	probePtCorrUp[0] = jet.ptCorrUp;
	probePtCorrDown[0] = jet.ptCorrDown;
	
	pair[0] = iTag;
	pair[1] = iJet;
	break;
      }
      if (pair[0] < photons.size())
	break;

    }
    if (pair[0] > photons.size())
      continue;
    
    // printf("Pass TnP pair selection\n");

    njets = 0;

    for (unsigned iJet(0); iJet != jets.size(); ++iJet) {
      if (iJet == pair[1])
	continue;
      auto& jet(jets[iJet]);
      if (jet.pt > 30.) {
	njets++;
	recoil += jet.p4();
      }
    }

    recoilPt = recoil.Pt();
    recoilEta = recoil.Eta();
    recoilPhi = recoil.Phi();
    recoilMass = recoil.M();

    weight = _sampleWeight * event.weight;
    if (_npvweight) {
      int iX(_npvweight->FindFixBin(event.npv));
      if (iX == 0)
	iX = 1;
      if (iX > _npvweight->GetNbinsX())
	iX = _npvweight->GetNbinsX();
      weight *= _npvweight->GetBinContent(iX);
    }

    output->Fill();
  }  
  
  outputFile->cd();
  output->Write();
  delete outputFile;

  printf("Finished skim.\n");
}
