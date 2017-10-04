#include "PandaTree/Objects/interface/Event.h"

#include "TTree.h"
#include "TH1D.h"

void
makeZGWGHistograms(TTree* _input, TH1D* _output)
{
  panda::Event event;
  event.setAddress(*_input, {"!*", "genParticles", "weight"});

  long iEntry(0);
  while (event.getEntry(*_input, iEntry++) > 0) {
    if (iEntry % 10000 == 1)
      std::cout << iEntry << std::endl;

    for (auto& part : event.genParticles) {
      if (part.pdgid != 22 || !part.finalState)
        continue;

      if (part.pt() < _output->GetXaxis()->GetXmin() || std::abs(part.eta()) > 1.4442)
        continue;

      auto* parent(part.parent.get());
      while (parent && parent->pdgid == 22) {
        if (parent->testFlag(panda::GenParticle::kFromHardProcess))
          break;
        parent = parent->parent.get();
      }

      if (!parent || parent->pdgid != 22)
        continue;
      
      _output->Fill(part.pt());
      break;
    }
  }
}
