#include "jer.h"

#include <fstream>
#include <string>

JER::JER(char const* _sourcePath)
{
  std::ifstream source(_sourcePath);

  std::string sdummy;
  source >> sdummy >> sdummy >> sdummy >> sdummy >> sdummy;
  source >> sdummy;
  formula_ = new TF1("formula", sdummy.c_str(), 15., 6500.);

  source >> sdummy;

  while (true) {
    double etaMin, etaMax, rhoMin, rhoMax, dummy;
    source >> etaMin;
    if (!source.good())
      break;

    source >> etaMax >> rhoMin >> rhoMax >> dummy;

    // rely on lines ordered in eta and rho

    unsigned iEta(0);
    for (; iEta != etaBinning_.size(); ++iEta) {
      if (etaBinning_[iEta].first < etaMin + 1.e-6 && etaBinning_[iEta].second > etaMax - 1.e-6)
        break;
    }
    if (iEta == etaBinning_.size())
      etaBinning_.emplace_back(etaMin, etaMax);

    unsigned iRho(0);
    for (; iRho != rhoBinning_.size(); ++iRho) {
      if (rhoBinning_[iRho].first < rhoMin + 1.e-6 && rhoBinning_[iRho].second > rhoMax - 1.e-6)
        break;
    }
    if (iRho == rhoBinning_.size())
      rhoBinning_.emplace_back(rhoMin, rhoMax);

    if (iEta >= params_.size())
      params_.resize(iEta + 1);
    if (iRho >= params_[iEta].size())
      params_[iEta].resize(iRho + 1);

    auto& params(params_[iEta][iRho]);
    source >> params.ptRange.first >> params.ptRange.second >> params.p0 >> params.p1 >> params.p2 >> params.p3;
  }
}

void
JER::scalefactor(double eta, double& sf, double& dsf) const
{
  double absEta(std::abs(eta));

  if (absEta < 0.8) {
    sf = 1.061;
    dsf = 0.023;
  }
  else if (absEta < 1.3) {
    sf = 1.088;
    dsf = 0.029;
  }
  else if (absEta < 1.9) {
    sf = 1.106;
    dsf = 0.030;
  }
  else if (absEta < 2.5) {
    sf = 1.126;
    dsf = 0.094;
  }
  else if (absEta < 3.) {
    sf = 1.343;
    dsf = 0.123;
  }
  else if (absEta < 3.2) {
    sf = 1.303;
    dsf = 0.111;
  }
  else {
    sf = 1.320;
    dsf = 0.286;
  }
}

double
JER::resolution(double pt, double eta, double rho) const
{
  unsigned iEta(0);
  if (eta < etaBinning_.front().first)
    iEta = 0;
  else if (eta >= etaBinning_.back().second)
    iEta = etaBinning_.size() - 1;
  else {
    for (; iEta != etaBinning_.size(); ++iEta) {
      auto& bin(etaBinning_[iEta]);
      if (bin.first <= eta && bin.second > eta)
        break;
    }
  }

  unsigned iRho(0);
  if (rho < rhoBinning_.front().first)
    iRho = 0;
  else if (rho >= rhoBinning_.back().second)
    iRho = rhoBinning_.size() - 1;
  else {
    for (; iRho != rhoBinning_.size(); ++iRho) {
      auto& bin(rhoBinning_[iRho]);
      if (bin.first <= rho && bin.second > rho)
        break;
    }
  }

  auto& params(params_[iEta][iRho]);
  if (pt < params.ptRange.first)
    pt = params.ptRange.first;
  else if (pt > params.ptRange.second)
    pt = params.ptRange.second;

  formula_->SetParameters(params.p0, params.p1, params.p2, params.p3);

  return formula_->Eval(pt) * pt;
}
