#include "TreeEntries_simpletree.h"

#include "TTree.h"
#include "TFile.h"
#include "TH1.h"
#include "TLorentzVector.h"
#include "math.h"

void
skim(TTree* _input, char const* _outputName, double _sampleWeight = 1., TH1* _npvweight = 0)
{
  printf("Running skim\n");

  simpletree::Event event;
  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"run", "lumi", "event", "weight", "npv", "electrons", "photons", "jets", "t1Met"});

  simpletree::Event outEvent;
  TFile* outputFile(TFile::Open(_outputName, "recreate"));
  TTree* output(new TTree("skim", "efficiency"));
  event.book(*output, {"run", "lumi", "event", "npv", "t1Met"});
  outEvent.book(*output, {"jets"});


  simpletree::PhotonCollection outProbe("probe");
  outProbe.init();

  double weight;

  float massTheo = 91.2;
  float massReco;
  float massCorr;

  float tagPt;
  float tagEta;
  float tagPhi;

  // float probePtCorr[1];

  float zPt;
  float zEta;
  float zPhi;

  unsigned short njets;
  short highPtIndex;
  bool pass;

  float recoilPt;
  float recoilEta;
  float recoilPhi;
  float recoilMass;

  /*
  output->Branch("run", &event.run, "run/i");
  output->Branch("lumi", &event.lumi, "lumi/i");
  output->Branch("event", &event.event, "event/i");
  output->Branch("npv", &event.npv, "npv/s");
  */

  output->Branch("weight", &weight, "weight/D");

  output->Branch("z.pt", &zPt, "z.pt/F");
  output->Branch("z.eta", &zEta, "z.eta/F");
  output->Branch("z.phi", &zPhi, "z.phi/F");
  output->Branch("z.mass", &massReco, "z.mass/F");
  // output->Branch("massCorr", &massCorr, "massCorr/F");

  output->Branch("tag.pt", &tagPt, "tag.pt/F");
  output->Branch("tag.eta", &tagEta, "tag.eta/F");
  output->Branch("tag.phi", &tagPhi, "tag.phi/F");

  outProbe.book(*output);
  
  // output->Branch("probe.ptCorr", probePtCorr, "probe.ptCorr[probe.size]/F");

  // output->Branch("njets", &njets, "njets/s");

  output->Branch("jets.highPtIndex", &highPtIndex, "jets.highPtIndex/s");

  output->Branch("recoil.pt", &recoilPt, "recoil.pt/F");
  output->Branch("recoil.eta", &recoilEta, "recoil.eta/F");
  output->Branch("recoil.phi", &recoilPhi, "recoil.phi/F");
  output->Branch("recoil.mass", &recoilMass, "recoil.mass/F");

  /*
  output->Branch("t1Met.met", &event.t1Met.met, "t1Met.met/F");
  output->Branch("t1Met.phi", &event.t1Met.phi, "t1Met.phi/F");
  output->Branch("t1Met.sumEt", &event.t1Met.sumEt, "t1Met.sumEt/F");
  */

  simpletree::LorentzVectorM probe;
  simpletree::LorentzVectorM zReco;
  simpletree::LorentzVectorM zCorr;

  simpletree::LorentzVectorM recoil;
  simpletree::LorentzVectorM met;

  float eleE;
  float elePx;
  float elePy;
  float elePz;

  float phoE;
  float phoPx;
  float phoPy;
  float phoPz;

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    if (iEntry % 1000000 == 0)
      printf("Event %ld\n", iEntry);
    
    auto& electrons(event.electrons);
    auto& photons(event.photons);
    auto& jets(event.jets);
    auto& t1Met(event.t1Met);
    
    probe.SetCoordinates(0.,0.,0.,0.);
    zReco.SetCoordinates(0.,0.,0.,0.);
    zCorr.SetCoordinates(0.,0.,0.,0.);

    recoil.SetCoordinates(0.,0.,0.,0.);
    met.SetCoordinates(t1Met.met, 0., t1Met.phi, 0.);

    unsigned pair[] = {unsigned(-1), unsigned(-1)};

    for (unsigned iEle(0); iEle != electrons.size(); ++iEle) {
      auto& ele(electrons[iEle]);
      if ( !(ele.tight && ele.pt > 30. && (ele.matchHLT23Loose || ele.matchHLT27Loose)))
	continue;

      // printf("Tag electron found\n");
      
      for (unsigned iPho(0); iPho != photons.size(); ++iPho) {
	auto& pho(photons[iPho]);
	if ( !(pho.medium && pho.pt > 20.))
	  continue;

	// printf("Medium photon found for probe\n");
	
	if (ele.dR2(pho) < 0.09)
	  continue;

	// printf("No photon/electron overlap\n");

	zReco = (ele.p4() + pho.p4());
	massReco = zReco.M();

	if ( !(massReco > 61. && massReco < 121.)) {
	  // printf("Z mass: %.2f\n", massReco);
	  continue;
	}
	

	// printf("On shell Z\n");

	tagPt = ele.pt;
	tagEta = ele.eta;
	tagPhi = ele.phi;

	outProbe.resize(1);
	outProbe[0] = pho;

	zPt = zReco.Pt();
	zEta = zReco.Eta();
	zPhi = zReco.Phi();

	/*
	eleE = ele.p4().E();
	elePx = ele.p4().Px();
	elePy = ele.p4().Py();
	elePz = ele.p4().Pz();

	phoE = pho.p4().E();
	phoPx = pho.p4().Px() / phoE;
	phoPy = pho.p4().Py() / phoE;
	phoPz = pho.p4().Pz() / phoE;

	probePtCorr[0] = (massTheo*massTheo/2) / (eleE - elePx*phoPx - elePy*phoPy - elePz*phoPz) / cosh(pho.eta); 
	probe.SetCoordinates(probePtCorr[0], pho.eta, pho.phi, 0.);	

	zCorr = (ele.p4() + probe);
	massCorr = zCorr.M();
        */

	pair[0] = iEle;
	pair[1] = iPho;
	break;

      }
      if (pair[0] < electrons.size())
	break;
    }
    if (pair[0] > electrons.size())
      continue;
    
    // printf("Pass TnP pair selection\n");

    njets = 0;
    pass = false;
    highPtIndex = -1;

    for (unsigned iJet(0); iJet != jets.size(); ++iJet) {
      auto& jet(jets[iJet]);
      if (jet.pt > 30.) {
	njets++;
	outEvent.jets.resize(njets);
	outEvent.jets[njets-1] = jet;
	// outEvent.jets.push_back(jet);
	recoil += jet.p4();
      }
      if (jet.pt > 100. && std::abs(TVector2::Phi_mpi_pi(jet.phi - zPhi)) > 2.5) {
	highPtIndex = njets-1;
	pass = true;
      }
    }

    if (!pass)
      continue;

    // printf("Z mass: %6.2f, jet mass: %6.2f\n", massReco, outEvent.jets[0].mass);

    /*
    if (recoil.Pt() < 170.)
      continue;
    */

    // printf("Pass recoil selection\n");

    /*
    if (std::abs(TVector2::Phi_mpi_pi(recoil.Phi() - zCorr.Phi())) < 2.5)
      continue;
    */

    // printf("Pass back-to-back requirement\n");

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
