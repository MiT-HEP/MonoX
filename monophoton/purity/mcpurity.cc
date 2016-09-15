#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TLorentzVector.h"
#include "TROOT.h"
#include "TEntryListArray.h"

#include "TreeEntries_simpletree.h"

#include "

class Skimmer {
public:
  Skimmer() {}
  double* calcMcEff(TTree* _input);

  void setMinPhoPt(float minPhoPt) { minPhoPt_ = minPhoPt; }
  void setMaxPhoPt(float maxPhoPt) { maxPhoPt_ = maxPhoPt; }
  void setMinMet(float minMet) { minMet_ = minMet; }
  void setMaxMet(float maxMet) { maxMet_ = maxMet; }
  void setMinMet(float minMet) { minMet_ = minMet; }
  void setMaxMet(float maxMet) { maxMet_ = maxMet; }
  
  void setMaxDR2(float maxDR2) { maxDR2_ = maxDR2; }
  void setMaxDPt(float maxDPt) { maxDPt_ = maxDPt; }

  void setWorkingPoint(unsigned wp) { wp_ = wp; }

private:
  float minPhoPt_{175.};
  float maxPhoPt_{6500.};
  float minMet_{0.};
  float maxMet_{60.};
  float minEta_{0.};
  float maxEta_{1.5};
  
  float maxDR2_{0.04};
  float maxDPt_{0.2};

  unsigned wp_{1};
};

double* 
Skimmer::calcMcEff(TTree* _input) {
  
  simpletree::Event event;
  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"run", "lumi", "event", "weight", "npv", "npvTrue", "photons", "t1Met"});

  double nGenPhotons(0.);
  unsigned iReco(0);
  unsigned nSteps(10);
  double nRecoPhotons[nSteps];
  for (iReco; iReco != nSteps; iReco++)
    nRecoPhotons[iReco] = 0.;

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    if (event.t1Met.met > maxMet_ || event.t1Met.met < minMet_)
      continue;

    auto& promptFinalStates(event.promptFinalStates);
    auto& photons(event.photons);

    for (unsigned iPFS(0); iPFS != promptFinalStates.size(); ++iPFS) {
      auto& pfs(promptFinalStates[iPFS]);
      
      if ( !(std::abs(pfs.pid) != 22))
	continue;

      // need to put some gen level pt / eta cuts here

      nGenPhotons++;
      
      for (unsigned iPho(0); iPho != photons.size(); ++iPho) {
	auto& pho(photons[iPho]);

	iReco = 0;
	nRecoPhotons[iReco]++;
	
	if (pfs.dR2(pho) > maxDR2_)
	  continue;

	iReco++;
	nRecoPhotons[iReco]++;
	
	if ( std::abs(pfs.pt - pho.pt) / pfs.pt  > maxDPt_)
	  continue;

	iReco++;
	nRecoPhotons[iReco]++;
	
	if ( pho.pt > maxPhoPt_ || pho.pt < minPhoPt_ )
	  continue;

	iReco++;
	nRecoPhotons[iReco]++;

	if ( pho.eta > maxEta_ || pho.eta < minEta_ )
	  continue;

	iReco++;
	nRecoPhotons[iReco]++;

	if ( !(pho.passHOverE(wp_) && pho.passSieie(wp_) && pho.passCHIso(wp_) && pho.passNHIso(wp_) && pho.passPhIso(wp_)))
	  continue;

	iReco++;
	nRecoPhotons[iReco]++;

	if (checkPixelVeto && !pho.pixelVeto)
	  continue;

	iReco++;
	nRecoPhotons[iReco]++;

	if (monophID && !( std::abs(_pho.time) < 3. && pho.mipEnergy < 4.9 && pho.sieie > 0.001 && pho.sipip > 0.001 && !(pho.eta > 0. && pho.eta < 0.15 && pho.phi > 0.527580 && pho.phi < 0.541795) && pho.chWorstIso < simpletree::Photon::chIsoCuts[0][wp_]))
	  continue;

	iReco++;
	nRecoPhotons[iReco]++;
      }
    }
  }

  double efficiencies[nSteps];
  for (iReco = 0; iReco != nSteps; iReco++)
    efficiencies[iReco] = nRecoPhotons[iReco] / nGenPhotons;

  return efficiencies;
}
