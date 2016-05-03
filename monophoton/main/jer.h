/*
  Horrible skim-level JER application..
  Only guaranteed to work with Summer15_25nsV6_MC_PtResolution_AK4PFchs.txt
*/
#ifndef JER_H
#define JER_H

#include <vector>
#include <utility>
#include "TF1.h"

class JER {
public:
  JER(char const* sourcePath);
  ~JER() { delete formula_; }

  void scalefactor(double eta, double& sf, double& dsf) const;
  double resolution(double pt, double eta, double rho) const; // return absolute resolution

  struct Params {
    std::pair<double, double> ptRange;
    double p0;
    double p1;
    double p2;
    double p3;
  };

private:
  std::vector<std::pair<double, double>> etaBinning_{};
  std::vector<std::pair<double, double>> rhoBinning_{};
  std::vector<std::vector<Params>> params_{}; // index [iEta][iRho]

  TF1* formula_{0};
};

#endif
