#include "PandaTree/Objects/interface/Event.h"

#include "TTree.h"
#include "TH1D.h"

void
makeZGWGHistograms(TTree* _input, TH1D* _poutput, TH1D* _noutput = 0)
{
  panda::Event event;
  event.setAddress(*_input, {"!*", "partons", "genParticles", "weight"});

  long iEntry(0);
  while (event.getEntry(*_input, iEntry++) > 0) {
    if (iEntry % 10000 == 1)
      std::cout << iEntry << std::endl;

    TH1D* out(_poutput);

    if (_noutput != 0) {
      // we are looking for charge-separated WG
      for (auto& part : event.partons) {
        if (part.pdgid == 11 || part.pdgid == 13 || part.pdgid == 15) {
          out = _noutput;
          break;
        }
      }
    }

    for (auto& part : event.genParticles) {
      if (part.pdgid != 22 || !part.finalState)
        continue;

      if (part.pt() < out->GetXaxis()->GetXmin() || std::abs(part.eta()) > 1.4442)
        continue;

      auto* parent(part.parent.get());
      while (parent && parent->pdgid == 22) {
        if (parent->testFlag(panda::GenParticle::kFromHardProcess))
          break;
        parent = parent->parent.get();
      }

      if (!parent || parent->pdgid != 22)
        continue;
      
      out->Fill(part.pt());
      break;
    }
  }
}
