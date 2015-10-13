#include "TMath.h"

inline Double_t magnitudeFunc (Double_t x, Double_t p0, Double_t p1) {
  return p0 * TMath::Exp(-1 * p1 * x);
}

inline Double_t Func (Double_t x, Double_t p0, Double_t p1, Double_t p2) {
  return p0 + p1 * x + p2 * TMath::Log(x);
}

inline Double_t Func (Double_t x, Double_t p0, Double_t p1) {
  return p0 + p1 * x;
}

Double_t quad (Double_t *x, Double_t *p) {
  return Func(x[0],p[0],p[1],p[2]);
}

Double_t lin (Double_t *x, Double_t *p) {
  return Func(x[0],p[0],p[1]);
}

Double_t fitFunc (Double_t *x, Double_t *p) {
  Double_t mu     = Func(x[0],p[0],p[1]);
  Double_t sigma3 = Func(x[0],p[2],p[3],p[4]);
  Double_t sigma1 = Func(x[0],p[5],p[6],p[7]);
  Double_t sigma2 = Func(x[0],p[8],p[9],p[10]);
  Double_t frac = (sigma3 - sigma1)/(sigma2 - sigma1);
  /* return magnitudeFunc(x[0],p[11],p[12]) * (frac/sigma1 * TMath::Gaus(x[1],mu,sigma1) + (1-frac)/sigma2 * TMath::Gaus(x[1],mu,sigma2)); */
  /* return Func(x[0],p[11],p[12]) * (frac/sigma1 * TMath::Gaus(x[1],mu,sigma1) + (1-frac)/sigma2 * TMath::Gaus(x[1],mu,sigma2)); */
  return 100*(frac/sigma1 * TMath::Gaus(x[1],mu,sigma1) + (1-frac)/sigma2 * TMath::Gaus(x[1],mu,sigma2));
}
