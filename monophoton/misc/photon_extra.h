#ifndef photon_extra_h
#define photon_extra_h

#include "Objects/interface/XPhoton.h"

namespace panda {

  void
  photon_extra(panda::XPhoton& _dest, panda::Photon const& _src, double rho)
  {
    auto& superCluster(*_src.superCluster);

    _dest.scRawPt = superCluster.rawPt;
    _dest.scEta = superCluster.eta;
    _dest.e4 = _src.eleft + _src.eright + _src.etop + _src.ebottom;
    _dest.isEB = std::abs(_dest.scEta) < 1.4442;

    // Recomputing isolation with scRawPt
    // S15 isolation valid only for panda >= 003
    // In 002 we had Spring15 leakage correction but Spring16 effective areas (production error).

    double chIsoEAS16(0.);
    double nhIsoEAS16(0.);
    double phIsoEAS16(0.);
    double nhIsoEAS15(0.);
    double phIsoEAS15(0.);
    double absEta(std::abs(_dest.scEta));
    if (absEta < 1.) {
      nhIsoEAS15 = 0.0599;
      phIsoEAS15 = 0.1271;
      chIsoEAS16 = 0.0360;
      nhIsoEAS16 = 0.0597;
      phIsoEAS16 = 0.1210;
    }
    else if (absEta < 1.479) {
      nhIsoEAS15 = 0.0819;
      phIsoEAS15 = 0.1101;
      chIsoEAS16 = 0.0377;
      nhIsoEAS16 = 0.0807;
      phIsoEAS16 = 0.1107;
    }
    else if (absEta < 2.) {
      nhIsoEAS15 = 0.0696;
      phIsoEAS15 = 0.0756;
      chIsoEAS16 = 0.0306;
      nhIsoEAS16 = 0.0629;
      phIsoEAS16 = 0.0699;
    }
    else if (absEta < 2.2) {
      nhIsoEAS15 = 0.0360;
      phIsoEAS15 = 0.1175;
      chIsoEAS16 = 0.0283;
      nhIsoEAS16 = 0.0197;
      phIsoEAS16 = 0.1056;
    }
    else if (absEta < 2.3) {
      nhIsoEAS15 = 0.0360;
      phIsoEAS15 = 0.1498;
      chIsoEAS16 = 0.0254;
      nhIsoEAS16 = 0.0184;
      phIsoEAS16 = 0.1457;
    }
    else if (absEta < 2.4) {
      nhIsoEAS15 = 0.0462;
      phIsoEAS15 = 0.1857;
      chIsoEAS16 = 0.0217;
      nhIsoEAS16 = 0.0284;
      phIsoEAS16 = 0.1719;
    }
    else {
      nhIsoEAS15 = 0.0656;
      phIsoEAS15 = 0.2183;
      chIsoEAS16 = 0.0167;
      nhIsoEAS16 = 0.0591;
      phIsoEAS16 = 0.1998;
    }

    double nhIsoE1S15, nhIsoE2S15, phIsoE1S15;
    double nhIsoE1S16, nhIsoE2S16, phIsoE1S16;

    if (_dest.isEB) {
      nhIsoE1S15 = 0.014;
      nhIsoE2S15 = 0.000019;
      phIsoE1S15 = 0.0053;

      nhIsoE1S16 = 0.0148;
      nhIsoE2S16 = 0.000017;
      phIsoE1S16 = 0.0047;
    }
    else {
      nhIsoE1S15 = 0.0139;
      nhIsoE2S15 = 0.000025;
      phIsoE1S15 = 0.0034;

      nhIsoE1S16 = 0.0163;
      nhIsoE2S16 = 0.000014;
      phIsoE1S16 = 0.0034;
    }

    double pt(_src.pt());
    double pt2(pt * pt);
    double scpt(_dest.scRawPt);
    double scpt2(scpt * scpt);

    double chIsoCore(_src.chIso + chIsoEAS16 * rho);
    double nhIsoCore(_src.nhIso + nhIsoEAS16 * rho + nhIsoE1S16 * pt + nhIsoE2S16 * pt2);
    double phIsoCore(_src.phIso + phIsoEAS16 * rho + phIsoE1S16 * pt);

    // _dest.chIso = chIsoCore - chIsoEAS16 * rho; // identity
    _dest.nhIso = nhIsoCore - nhIsoEAS16 * rho - nhIsoE1S16 * scpt - nhIsoE2S16 * scpt2;
    _dest.phIso = phIsoCore - phIsoEAS16 * rho - phIsoE1S16 * scpt;

    _dest.loose = _dest.passHOverE(0, 0) && _dest.passSieie(0, 0) &&
      _dest.passCHIso(0) && _dest.passNHIso(0) && _dest.passCHIso(0);
    _dest.medium = _dest.passHOverE(1, 0) && _dest.passSieie(1, 0) &&
      _dest.passCHIso(1) && _dest.passNHIso(1) && _dest.passCHIso(1);
    _dest.tight = _dest.passHOverE(2, 0) && _dest.passSieie(2, 0) &&
      _dest.passCHIso(2) && _dest.passNHIso(2) && _dest.passCHIso(2);

    _dest.chIsoS15 = chIsoCore;        
    _dest.nhIsoS15 = nhIsoCore - nhIsoEAS15 * rho - nhIsoE1S15 * scpt - nhIsoE2S15 * scpt2;
    _dest.phIsoS15 = phIsoCore - nhIsoEAS15 * rho - phIsoE1S15 * scpt;

    // EA computed with iso/worstIsoEA.py
    _dest.chIsoMax -= 0.094 * rho;
    if (_dest.chIsoMax < _dest.chIso)
      _dest.chIsoMax = _dest.chIso;

    if (_src.matchedGen.isValid()) {
      _dest.matchedGenId = _src.matchedGen->pdgid;
      if (_dest.matchedGenId == 22) {
        auto& gen(*_src.matchedGen);
        if (gen.testFlag(panda::GenParticle::kIsPrompt) ||
            (gen.parent.isValid() && gen.parent->pdgid == 22 && gen.parent->testFlag(panda::GenParticle::kIsPrompt)))
          _dest.matchedGenId = -22;
      }
    }
  }

}

#endif
