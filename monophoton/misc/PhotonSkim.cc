#include "Objects/interface/Event.h"
#include "Utils/interface/FileMerger.h"

#include "GoodLumiFilter.h"

#include "TString.h"

#include <cmath>

void
PhotonSkim(char const* _sourceDir, char const* _outputPath, long _nEvents = -1, GoodLumiFilter* _goodlumi = 0)
{
  panda::FileMerger merger;

  panda::FileMerger::SkimFunction skim;
  
  if (_goodlumi) {
    skim = [_goodlumi](panda::Event& _event)->bool {
      if (!_goodlumi->isGoodLumi(_event.runNumber, _event.lumiNumber))
        return false;
  
      for (auto& photon : _event.photons) {
        if (std::abs(photon.superCluster->eta) < 1.4442 && photon.superCluster->rawPt > 150.)
          return true;
      }
      return false;
    };
  }
  else {
    skim = [](panda::Event& _event)->bool {
      for (auto& photon : _event.photons) {
        if (std::abs(photon.superCluster->eta) < 1.4442 && photon.superCluster->rawPt > 150.)
          return true;
      }
      return false;
    };
  }

  TString sourcePath(_sourceDir);
  sourcePath += "/*.root";

  merger.addInput(sourcePath);
  merger.selectBranches({"!pfCandidates", "!puppiAK4Jets", "!chsAK8Jets", "!puppiAK8Jets", "!chsCA15Jets", "!puppiCA15Jets", "!subjets"}, true);
  merger.setSkim(skim);

  merger.merge(_outputPath, _nEvents);
}
