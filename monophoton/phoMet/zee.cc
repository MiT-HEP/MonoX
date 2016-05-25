#include "TreeEntries_simpletree.h"

#include "TTree.h"
#include "TFile.h"
#include "TH1.h"
#include "TLorentzVector.h"
#include "math.h"

void
zee(TTree* _input, char const* _outputName, double _sampleWeight = 1., TH1* _npvweight = 0)
{
  printf("Running skim\n");

  simpletree::Event event;
  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"run", "lumi", "event", "weight", "npv", "muons", "electrons", "photons", "jets", "t1Met"});

  simpletree::Event outEvent;
  TFile* outputFile(TFile::Open(_outputName, "recreate"));
  TTree* output(new TTree("skim", "efficiency"));
  event.book(*output, {"run", "lumi", "event", "npv", "t1Met"});
  outEvent.book(*output, {"jets"});

  double weight;

  float massReco;

  float tagPt;
  float tagEta;
  float tagPhi;
  bool tagPos;

  float probePt;
  float probeEta;
  float probePhi;
  bool probePos;

  float zPt;
  float zEta;
  float zPhi;
  bool zOppSign;

  unsigned short njets;
  bool pass;

  float minJetDPhi;

  output->Branch("weight", &weight, "weight/D");

  output->Branch("z.pt", &zPt, "z.pt/F");
  output->Branch("z.eta", &zEta, "z.eta/F");
  output->Branch("z.phi", &zPhi, "z.phi/F");
  output->Branch("z.mass", &massReco, "z.mass/F");
  output->Branch("z.oppSign", &zOppSign, "z.oppSign/O");

  output->Branch("tag.pt", &tagPt, "tag.pt/F");
  output->Branch("tag.eta", &tagEta, "tag.eta/F");
  output->Branch("tag.phi", &tagPhi, "tag.phi/F");
  output->Branch("tag.positive", &tagPos, "tag.positive/O");

  output->Branch("probe.pt", &probePt, "probe.pt/F");
  output->Branch("probe.eta", &probeEta, "probe.eta/F");
  output->Branch("probe.phi", &probePhi, "probe.phi/F");
  output->Branch("probe.positive", &probePos, "probe.positive/O");

  output->Branch("t1Met.minJetDPhi", &minJetDPhi, "t1Met.minJetDPhi/F");

  simpletree::LorentzVectorM probe;
  simpletree::LorentzVectorM zReco;

  simpletree::LorentzVectorM met;

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    if (iEntry % 1000000 == 0)
      printf("Event %ld\n", iEntry);
    
    auto& electrons(event.electrons);
    auto& jets(event.jets);
    auto& t1Met(event.t1Met);
    
    probe.SetCoordinates(0.,0.,0.,0.);
    zReco.SetCoordinates(0.,0.,0.,0.);

    met.SetCoordinates(t1Met.met, 0., t1Met.phi, 0.);

    unsigned pair[] = {unsigned(-1), unsigned(-1)};

    for (unsigned iTag(0); iTag != electrons.size(); ++iTag) {
      auto& tag(electrons[iTag]);
      if ( !(tag.tight && tag.pt > 30.))
	continue;

      //printf("Tag electron found\n");
      
      for (unsigned iProbe(iTag); iProbe != electrons.size(); ++iProbe) {
	auto& probe(electrons[iProbe]);
	if ( !(probe.loose && probe.pt > 20.))
	  continue;

	//printf("Loose electron found for probe\n");
	
	zReco = (tag.p4() + probe.p4());
	massReco = zReco.M();

	if ( !(massReco > 61. && massReco < 121.)) {
	  // printf("Z mass: %.2f\n", massReco);
	  continue;
	}

	//printf("On shell Z\n");

	tagPt = tag.pt;
	tagEta = tag.eta;
	tagPhi = tag.phi;
	tagPos = tag.positive;

	probePt = probe.pt;
	probeEta = probe.eta;
	probePhi = probe.phi;
	probePos = probe.positive;

	zPt = zReco.Pt();
	zEta = zReco.Eta();
	zPhi = zReco.Phi();
	zOppSign = ( (tag.positive == probe.positive) ? 0 : 1);

	pair[0] = iTag;
	pair[1] = iProbe;
	break;

      }
      if (pair[0] < electrons.size())
	break;
    }
    if (pair[0] > electrons.size())
      continue;
    
    //printf("Pass TnP pair selection\n");

    njets = 0;
    pass = false;
    minJetDPhi = 4.;

    for (unsigned iJet(0); iJet != jets.size(); ++iJet) {
      auto& jet(jets[iJet]);
      if (jet.pt > 30. ) {
	njets++;
	outEvent.jets.resize(njets);
	outEvent.jets[njets-1] = jet;
	// outEvent.jets.push_back(jet);
	if (njets < 5. && TMath::Abs(TVector2::Phi_mpi_pi(jet.phi - t1Met.phi)) < minJetDPhi )
	  minJetDPhi = TMath::Abs(TVector2::Phi_mpi_pi(jet.phi - t1Met.phi));
	if (std::abs(TVector2::Phi_mpi_pi(jet.phi - zPhi)) > 2.5)
	  pass = true;
      }
    }

    if (!pass)
      continue;

    // printf("tag charge %d, probe charge %d, opp sign %d \n", tagPos, probePos, zOppSign);

    // printf("Pass jet selection.\n");

    
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
    // printf("Filled\n");
  }  
  
  outputFile->cd();
  output->Write();
  delete outputFile;
  
  printf("Finished skim.\n");
}
