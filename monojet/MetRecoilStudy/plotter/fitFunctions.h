#include "TMath.h"

inline Double_t Func (Double_t x, Double_t p0, Double_t p1, Double_t p2, Double_t p3) {
  return p0 + p1 * x + p2 * TMath::Log(x) + p3 * x * x;
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

/* Double_t fitFunc (Double_t *x, Double_t *p) { */
/*   Double_t mu     = Func(x[0],p[0],p[1]); */
/*   Double_t sigma3 = Func(x[0],p[2],p[3],p[4]); */
/*   Double_t sigma1 = Func(x[0],p[5],p[6],p[7]); */
/*   Double_t sigma2 = Func(x[0],p[8],p[9],p[10]); */
/*   Double_t frac = (sigma3 - sigma1)/(sigma2 - sigma1); */
/*   return frac/sigma1 * TMath::Gaus(x[1],mu,sigma1) + (1-frac)/sigma2 * TMath::Gaus(x[1],mu,sigma2); */
/* } */

Double_t fitFunc (Double_t *x, Double_t *p) {
  Double_t mu     = Func(x[0],p[0],p[1]);
  Double_t sigma3 = p[2];
  Double_t sigma1 = p[3];
  Double_t sigma2 = p[4];
  Double_t frac = (sigma3 - sigma1)/(sigma2 - sigma1);
  return frac/sigma1 * TMath::Gaus(x[1],mu,sigma1) + (1-frac)/sigma2 * TMath::Gaus(x[1],mu,sigma2);
}

Double_t singleFunc (Double_t *x, Double_t *p) {
  Double_t mu     = Func(x[0],p[0],p[1]);
  Double_t sigma1 = Func(x[0],p[2],p[3],p[4]);
  return TMath::Gaus(x[1],mu,sigma1)/sigma1;
}
