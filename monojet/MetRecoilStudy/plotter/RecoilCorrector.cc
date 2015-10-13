#include "RecoilCorrector.h"
#include "TVector2.h"

RecoilCorrector::RecoilCorrector() :
  fSingleGaus(false)
{
  rng = new TRandom3();
  inName = "Zmm";
  outName = "Wjets";
}

RecoilCorrector::~RecoilCorrector() { 
 for (unsigned int iR=0; iR!=3; ++iR) {
   for (unsigned int iU=0; iU!=2; ++iU) {
    if (covMu[iU][iR])
      delete covMu[iU][iR];
    if (covSigma1[iU][iR])
      delete covSigma1[iU][iR];
    if (covSigma2[iU][iR])
      delete covSigma2[iU][iR];
    if (covSigma[iU][iR])
      delete covSigma[iU][iR];
    if (covSigmaSingle[iU][iR])
      delete covSigmaSingle[iU][iR];
   }
  } 

  delete rng;
}

void RecoilCorrector::SetFitResult(TF1 *f, TMatrixDSym *cov, RecoilType rType, UType uType, Parameter p) {
  // Store pointer to fit function and recover covariance matrix of fit
  // For now, f cannot be deleted until RecoilCorrector is done running
  // TODO: clone f parameters and store locally, involves assuming poly
  // form of f
  switch (p) {
    case kMu:
      fmu[uType][rType] = f;
      covMu[uType][rType] = (TMatrixDSym*)cov->Clone();
      if (!xxMu)
        xxMu = new double[covMu[uType][rType]->GetNrows()];
      break;
    case kSigma1:
      fsigma1[uType][rType] = f;
      covSigma1[uType][rType] =  (TMatrixDSym*)cov->Clone();
      if (!xxSigma1)
        xxSigma1 = new double[covSigma1[uType][rType]->GetNrows()];
      break;
    case kSigma2:
      fsigma2[uType][rType] = f;
      covSigma2[uType][rType] =  (TMatrixDSym*)cov->Clone();
      if (!xxSigma2)
        xxSigma2 = new double[covSigma2[uType][rType]->GetNrows()];
      break;
    case kSigma:
      fsigma[uType][rType] = f;
      covSigma[uType][rType] =  (TMatrixDSym*)cov->Clone();
      if (!xxSigma)
        xxSigma = new double[covSigma[uType][rType]->GetNrows()];
      break;
    case kSigmaSingle:
      fsigmaSingle[uType][rType] = f;
      covSigmaSingle[uType][rType] =  (TMatrixDSym*)cov->Clone();
      if (!xxSigmaSingle)
        xxSigmaSingle = new double[covSigmaSingle[uType][rType]->GetNrows()];
      break;
  }
}

void RecoilCorrector::LoadAllFits(TFile *fIn) {
  TString fitBaseName;
  TString recoilNames[3] = {"Data_"+inName,"MC_"+inName,"MC_"+outName};
  TF1 *f;
  TMatrixDSym *cov;
  fprintf(stderr,"RecoilCorrector::LoadAllFits: Careful not to close %s until you are done with RecoilCorrector.\n",fIn->GetName());
  for (unsigned int iR=0; iR!=3; ++iR) {
    for (int iU=0; iU!=2; ++iU) {
      fitBaseName = TString::Format("u%i_%s",iU+1,recoilNames[iR].Data());
      fprintf(stderr,"loading %s\n",fitBaseName.Data()); 
      
      f = (TF1*)fIn->Get("fcn_mu_"+fitBaseName);
      cov = (TMatrixDSym*)fIn->Get("cov_mu_"+fitBaseName);
      SetFitResult(f,cov,(RecoilType)iR,(UType)iU,kMu);      

      f = (TF1*)fIn->Get("fcn_sig1_"+fitBaseName);
      cov = (TMatrixDSym*)fIn->Get("cov_sig1_"+fitBaseName);
      SetFitResult(f,cov,(RecoilType)iR,(UType)iU,kSigma1);      
      
      f = (TF1*)fIn->Get("fcn_sig2_"+fitBaseName);
      cov = (TMatrixDSym*)fIn->Get("cov_sig2_"+fitBaseName);
      SetFitResult(f,cov,(RecoilType)iR,(UType)iU,kSigma2);      
      
      f = (TF1*)fIn->Get("fcn_sig3_"+fitBaseName);
      cov = (TMatrixDSym*)fIn->Get("cov_sig3_"+fitBaseName);
      SetFitResult(f,cov,(RecoilType)iR,(UType)iU,kSigma);      

      f = (TF1*)fIn->Get("fcn_sig_"+fitBaseName);
      cov = (TMatrixDSym*)fIn->Get("cov_sig_"+fitBaseName);
      SetFitResult(f,cov,(RecoilType)iR,(UType)iU,kSigmaSingle);      
    } // loop over u1 u2
  } // loop over recoil types
}

double RecoilCorrector::GetError(double x,RecoilType r,UType u,Parameter p) const {
  TMatrixDSym *cov = 0;
  double *xx = 0;
  switch (p) {
    case kMu:
      cov = covMu[u][r];
      xx = xxMu;
      break;
    case kSigma1:
      cov = covSigma1[u][r];
      xx = xxSigma1;
      break;
    case kSigma2:
      cov = covSigma2[u][r];
      xx = xxSigma2;
      break;
    case kSigma:
      cov = covSigma[u][r];
      xx = xxSigma;
      break;
    case kSigmaSingle:
      cov = covSigmaSingle[u][r];
      xx = xxSigmaSingle;
      break;
  }

  unsigned int dim = cov->GetNrows(); 
  
  for (unsigned int iR=0; iR!=dim; ++dim) 
    xx[iR] = TMath::Power(x,(Int_t)iR);

  double error=0;
  for (unsigned int iR=0; iR!=dim; ++iR) {
    error += xx[iR] * xx[iR] * (*cov)(iR,iR);
    for (unsigned int iC=0; iC!=iR; ++iC) {
      error += 2* xx[iC] * (*cov)(iC,iR) * xx[iR];
    }
  }

  return error;
}

void RecoilCorrector::ComputeU(float genpt, float &u1, float &u2, float nsigma/*=0*/) const {
  
  // first compute u1
  //double mu     = (fmu[kU1][kDataIn]->Eval(genpt))     * (fmu[kU1][kMCOut]->Eval(genpt))     / (fmu[kU1][kMCIn]->Eval(genpt));
  double mu     = (fmu[kU1][kDataIn]->Eval(genpt)-genpt)     * (fmu[kU1][kMCOut]->Eval(genpt)-genpt)     / (fmu[kU1][kMCIn]->Eval(genpt)-genpt);
  double sigma1 = fsigma1[kU1][kDataIn]->Eval(genpt) * fsigma1[kU1][kMCOut]->Eval(genpt) / fsigma1[kU1][kMCIn]->Eval(genpt);
  double sigma2 = fsigma2[kU1][kDataIn]->Eval(genpt) * fsigma2[kU1][kMCOut]->Eval(genpt) / fsigma2[kU1][kMCIn]->Eval(genpt);
  double sigma  = fsigma[kU1][kDataIn]->Eval(genpt)  * fsigma[kU1][kMCOut]->Eval(genpt)  / fsigma[kU1][kMCIn]->Eval(genpt);
  double sigmaSingle  = fsigmaSingle[kU1][kDataIn]->Eval(genpt)  * fsigmaSingle[kU1][kMCOut]->Eval(genpt)  / fsigmaSingle[kU1][kMCIn]->Eval(genpt);

  // a la error propogation used in w/z analaysis
  // TODO: improve to treat parameters independently
  // currently making conservative assumption of maximal correlation
  if (nsigma != 0.) {
    mu     += nsigma * GetError(genpt,kMCOut,kU1,kMu)     * fmu[kU1][kDataIn]->Eval(genpt)     / fmu[kU1][kMCIn]->Eval(genpt);
    sigma1 += nsigma * GetError(genpt,kMCOut,kU1,kSigma1) * fsigma1[kU1][kDataIn]->Eval(genpt) / fsigma1[kU1][kMCIn]->Eval(genpt); 
    sigma2 += nsigma * GetError(genpt,kMCOut,kU1,kSigma2) * fsigma2[kU1][kDataIn]->Eval(genpt) / fsigma2[kU1][kMCIn]->Eval(genpt);
    sigma  += nsigma * GetError(genpt,kMCOut,kU1,kSigma)  * fsigma[kU1][kDataIn]->Eval(genpt)  / fsigma[kU1][kMCIn]->Eval(genpt);
    sigmaSingle  += nsigma * GetError(genpt,kMCOut,kU1,kSigmaSingle)  * fsigmaSingle[kU1][kDataIn]->Eval(genpt)  / fsigmaSingle[kU1][kMCIn]->Eval(genpt);
  }

  double frac = (sigma-sigma2)/(sigma1-sigma2);

  if (fSingleGaus)
    u1 = rng->Gaus(mu,sigmaSingle);
  else
    u1 = (((rng->Uniform(0,1)<frac) ? rng->Gaus(mu,sigma1) : rng->Gaus(mu,sigma2)));

  // now compute u2
  mu     = fmu[kU2][kDataIn]->Eval(genpt)     * fmu[kU2][kMCOut]->Eval(genpt)     / fmu[kU2][kMCIn]->Eval(genpt);
  sigma1 = fsigma1[kU2][kDataIn]->Eval(genpt) * fsigma1[kU2][kMCOut]->Eval(genpt) / fsigma1[kU2][kMCIn]->Eval(genpt);
  sigma2 = fsigma2[kU2][kDataIn]->Eval(genpt) * fsigma2[kU2][kMCOut]->Eval(genpt) / fsigma2[kU2][kMCIn]->Eval(genpt);
  sigma  = fsigma[kU2][kDataIn]->Eval(genpt)  * fsigma[kU2][kMCOut]->Eval(genpt)  / fsigma[kU2][kMCIn]->Eval(genpt);
  sigmaSingle  = fsigmaSingle[kU2][kDataIn]->Eval(genpt)  * fsigmaSingle[kU2][kMCOut]->Eval(genpt)  / fsigmaSingle[kU2][kMCIn]->Eval(genpt);
  
  if (nsigma != 0.) {
    mu     += nsigma * GetError(genpt,kMCOut,kU2,kMu)     * fmu[kU2][kDataIn]->Eval(genpt)     / fmu[kU2][kMCIn]->Eval(genpt);
    sigma1 += nsigma * GetError(genpt,kMCOut,kU2,kSigma1) * fsigma1[kU2][kDataIn]->Eval(genpt) / fsigma1[kU2][kMCIn]->Eval(genpt); 
    sigma2 += nsigma * GetError(genpt,kMCOut,kU2,kSigma2) * fsigma2[kU2][kDataIn]->Eval(genpt) / fsigma2[kU2][kMCIn]->Eval(genpt);
    sigma  += nsigma * GetError(genpt,kMCOut,kU2,kSigma)  * fsigma[kU2][kDataIn]->Eval(genpt)  / fsigma[kU2][kMCIn]->Eval(genpt);
    sigmaSingle  += nsigma * GetError(genpt,kMCOut,kU2,kSigmaSingle)  * fsigmaSingle[kU2][kDataIn]->Eval(genpt)  / fsigmaSingle[kU2][kMCIn]->Eval(genpt);
  }

  frac = (sigma-sigma2)/(sigma1-sigma2);

  if (fSingleGaus)
    u2 = rng->Gaus(mu,sigmaSingle);
  else
    u2 = (rng->Uniform(0,1)<frac) ? rng->Gaus(mu,sigma1) : rng->Gaus(mu,sigma2);
}

void RecoilCorrector::CorrectMET(float genpt,float genphi,float leppt,float lepphi,float& met,float& metphi, float nsigma, float u1, float u2) const {
  if (u1==-999||u2==-999)
    ComputeU(genpt,u1,u2,nsigma);
  TVector2 vLep(leppt*TMath::Cos(lepphi),leppt*TMath::Sin(lepphi));
  TVector2 vU(u1*TMath::Cos(genphi)-u2*TMath::Sin(genphi),u1*TMath::Sin(genphi)+u2*TMath::Cos(genphi));
  TVector2 vMissingEnergy = -1*(vLep+vU);
  met = vMissingEnergy.Mod();
  metphi = vMissingEnergy.Phi();
}
