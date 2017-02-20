#include "Objects/interface/EventMonophoton.h"
#include "Utils/interface/FileMerger.h"

#include "GoodLumiFilter.h"

#include "TString.h"

#include <cmath>

class PhotonSkimmer {
public:
  PhotonSkimmer();
  void addSourcePath(char const* path) { merger_.addInput(path); }
  void run(char const*, long = -1, GoodLumiFilter* = 0);

private:
  panda::FileMerger merger_;
};

PhotonSkimmer::PhotonSkimmer()
{
  merger_.setPrintLevel(1);
  merger_.setInputTimeout(600);
}

void
PhotonSkimmer::run(char const* _outputPath, long _nEvents/* = -1*/, GoodLumiFilter* _goodlumi/* = 0*/)
{
  panda::EventMonophoton outEvent;
  merger_.setOutEvent(&outEvent);

  panda::FileMerger::SkimFunction skim([&outEvent, _goodlumi](panda::Event& _event)->bool {
      if (_goodlumi && !_goodlumi->isGoodLumi(_event.runNumber, _event.lumiNumber))
        return false;

      unsigned iPh(0);
      for (; iPh != _event.photons.size(); ++iPh) {
        auto& photon(_event.photons[iPh]);
        if (std::abs(photon.superCluster->eta) < 1.4442 && photon.superCluster->rawPt > 150.)
          break;
      }
      if (iPh == _event.photons.size())
        return false;

      outEvent = _event;
  
      for (unsigned iPh(0); iPh != _event.photons.size(); ++iPh) {
        auto& inPhoton(_event.photons[iPh]);
        auto& superCluster(*inPhoton.superCluster);
        auto& outPhoton(outEvent.photons[iPh]);

        outPhoton.scRawPt = superCluster.rawPt;
        outPhoton.scEta = superCluster.eta;
        outPhoton.e4 = inPhoton.eleft + inPhoton.eright + inPhoton.etop + inPhoton.ebottom;
        outPhoton.isEB = std::abs(outPhoton.scEta) < 1.4442;
      
        double chIsoS16EA(0.);
        double nhIsoS16EA(0.);
        double phIsoS16EA(0.);
        double nhIsoS15EA(0.);
        double phIsoS15EA(0.);
        double absEta(std::abs(outPhoton.scEta));
        if (absEta < 1.) {
          nhIsoS15EA = 0.0599;
          phIsoS15EA = 0.1271;
          chIsoS16EA = 0.0360;
          nhIsoS16EA = 0.0597;
          phIsoS16EA = 0.1210;
        }
        else if (absEta < 1.479) {
          nhIsoS15EA = 0.0819;
          phIsoS15EA = 0.1101;
          chIsoS16EA = 0.0377;
          nhIsoS16EA = 0.0807;
          phIsoS16EA = 0.1107;
        }
        else if (absEta < 2.) {
          nhIsoS15EA = 0.0696;
          phIsoS15EA = 0.0756;
          chIsoS16EA = 0.0306;
          nhIsoS16EA = 0.0629;
          phIsoS16EA = 0.0699;
        }
        else if (absEta < 2.2) {
          nhIsoS15EA = 0.0360;
          phIsoS15EA = 0.1175;
          chIsoS16EA = 0.0283;
          nhIsoS16EA = 0.0197;
          phIsoS16EA = 0.1056;
        }
        else if (absEta < 2.3) {
          nhIsoS15EA = 0.0360;
          phIsoS15EA = 0.1498;
          chIsoS16EA = 0.0254;
          nhIsoS16EA = 0.0184;
          phIsoS16EA = 0.1457;
        }
        else if (absEta < 2.4) {
          nhIsoS15EA = 0.0462;
          phIsoS15EA = 0.1857;
          chIsoS16EA = 0.0217;
          nhIsoS16EA = 0.0284;
          phIsoS16EA = 0.1719;
        }
        else {
          nhIsoS15EA = 0.0656;
          phIsoS15EA = 0.2183;
          chIsoS16EA = 0.0167;
          nhIsoS16EA = 0.0591;
          phIsoS16EA = 0.1998;
        }

        outPhoton.chIsoS15 = inPhoton.chIso;
        if (outPhoton.isEB) {
          outPhoton.nhIsoS15 = inPhoton.nhIso + (0.014 - 0.0148) * inPhoton.pt() + (0.000019 - 0.000017) * inPhoton.pt() * inPhoton.pt();
          outPhoton.phIsoS15 = inPhoton.phIso + (0.0053 - 0.0047) * inPhoton.pt();
        }
        else {
          outPhoton.nhIsoS15 = inPhoton.nhIso + (0.0139 - 0.0163) * inPhoton.pt() + (0.000025 - 0.000014) * inPhoton.pt() * inPhoton.pt();
          outPhoton.phIsoS15 = inPhoton.phIso + (0.0034 - 0.0034) * inPhoton.pt();
        }

        outPhoton.chIsoS15 += chIsoS16EA * _event.rho;
        outPhoton.nhIsoS15 += (nhIsoS15EA - nhIsoS16EA) * _event.rho;
        outPhoton.phIsoS15 += (phIsoS15EA - phIsoS16EA) * _event.rho;

        // EA computed with iso/worstIsoEA.py
        outPhoton.chIsoMax -= 0.094 * _event.rho;
        if (outPhoton.chIsoMax < outPhoton.chIso)
          outPhoton.chIsoMax = outPhoton.chIso;
      }

      return true;
    });

  merger_.setSkim(skim);

  panda::utils::BranchList branchList = {
    "!pfCandidates",
    "!puppiAK4Jets",
    "!chsAK8Jets",
    "!chsAK8Subjets",
    "!puppiAK8Jets",
    "!puppiAK8Subjets",
    "!chsCA15Jets",
    "!chsCA15Subjets",
    "!puppiCA15Jets",
    "!puppiCA15Subjets",
    "!subjets",
    "!ak8GenJets",
    "!ca15GenJets",
    "!puppiMet",
    "!rawMet",
    "!caloMet",
    "!noMuMet",
    "!noHFMet",
    "!trkMet",
    "!neutralMet",
    "!photonMet",
    "!hfMet",
    "!reoil",
    "t1Met",
    "jets",
    "genJets",
    "photons"
  };

  merger_.selectBranches(branchList, true);

  merger_.merge(_outputPath, _nEvents);
}
