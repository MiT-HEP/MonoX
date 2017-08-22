#include "TH1D.h"
#include "TVirtualFitter.h"
#include "TCanvas.h"
#include "TLatex.h"
#include "TROOT.h"
#include "TTree.h"

#include <iostream>
#include <cmath>

/*
  Signal subtraction simultaneous fitter

  Setup:
   - Target: A data distribution in SR.
   - Signal template: An MC distribution for signal shape to be extracted from target.
   - Background template: A data distribution obtained from some CR, representing the background in the SR. May contain some signal.
   - Signal CR template: An MC distribution taken from the same sample as signal template, but with the background template CR selection.
   - CR/SR ratio: The ratio of signal yields in CR and SR.
  
  Normalized target distribution g_0 is fitted by a linear combination of the signal and background templates. Signal component in the
  background template must be subtracted consistently.
  Let g_s, g_s', and g_b respectively be the normalized signal, signal CR, and background templates, f the fraction of signal events
  (fit parameter), N and B the original number of events in the target and the background template, and R the CR/SR ratio. The distribution
  to be compared against the target is

    f * g_s + (1-f) * (B * g_b - R*N*f * g_s') / int(B * g_b - R*N*f * g_s')

  The second term may need an explanation: R*N*f is the total number of signal events to be subtracted from the background template.
  B * g_b - R*N*f * g_s' is then the unnormalized signal-subtracted distribution from the CR. The denominator is the integral
  of this distribution, which is actually

    int(B * g_b - R*N*f * g_s') = B - R*N*f

  because by definition int(g_b) = int(g_s') = 1. Therefore the expression reduces to

    f * g_s + (1-f) * (g_b - R/B*N*f * g_s') / (1 - R/B*N*f)
*/

class SSFitter {
public:
  SSFitter() { gROOT->mkdir("SSFitter"); }
  ~SSFitter() {}

  void initialize(TH1* target, TH1* signalTemplate, TH1* bkgTemplate, TH1* signalCRTemplate, double CROverSR);
  void scaleSignal(TTree* t, char const* expr, char const* sel);
  void scaleSignalCR(TTree* t, char const* expr, char const* sel);
  void fit();
  
  double fcn(double* xval);

  double getPurity(int cutBin) const;
  double getNsig(int cutBin) const;
  double getNbkg(int cutBin) const;
  void preparePlot();
  void plotOn(TCanvas*);

  TH1* getTarget() { return target_; }
  TH1* getTotal() { return total_; }
  TH1* getSignal() { return signalTemplate_; }
  TH1* getBackground() { return bkgTemplate_; }
  TH1* getSubtractedBackground() { return subtractedBkg_; }
  

  static SSFitter* singleton();

private:
  static void FCN(int&, double*, double& fval, double* xval, int);

  void refillSignalTemplate(double a0, double a1);
  void refillSignalCRTemplate(double a0, double a1);

  TH1* target_{0};
  TH1* signalTemplate_{0};
  TH1* bkgTemplate_{0};
  TH1* signalCRTemplate_{0};

  // x values of the signal template when floating the linear transform of the signal x values
  std::vector<std::pair<double, double>> signalEvents_;
  std::vector<std::pair<double, double>> signalCREvents_;

  double ROverB_{0.};
  double nTarg_{0.};
  double nCR_{0.};

  double fsig_{0.};

  // temporary histograms for visualization
  TH1* total_{0};
  TH1* subtractedBkg_{0};
};

void
SSFitter::initialize(TH1* target, TH1* signalTemplate, TH1* bkgTemplate, TH1* signalCRTemplate, double CROverSR)
{
  delete target_;
  delete signalTemplate_;
  delete bkgTemplate_;
  delete signalCRTemplate_;

  gROOT->cd("SSFitter");
  target_ = (TH1*)target->Clone();
  signalTemplate_ = (TH1*)signalTemplate->Clone();
  bkgTemplate_ = (TH1*)bkgTemplate->Clone();
  signalCRTemplate_ = (TH1*)signalCRTemplate->Clone();

  std::cout << "B = " << bkgTemplate_->GetSumOfWeights() << std::endl;
  std::cout << "Max subtraction = " << (target_->GetSumOfWeights() * CROverSR) << std::endl;

  ROverB_ = CROverSR / bkgTemplate_->GetSumOfWeights();

  nTarg_ = target->GetSumOfWeights();
}

void
SSFitter::scaleSignal(TTree* t, char const* expr, char const* sel)
{
  std::cout << "Taking unbinned input for signal template from " << expr << " (" << sel << ")" << std::endl;

  signalEvents_.clear();

  t->SetEstimate(t->GetEntries() + 1);
  long nEntries(t->Draw(TString::Format("%s:weight", expr), sel, "goff"));
  for (long iEntry(0); iEntry < nEntries; ++iEntry)
    signalEvents_.emplace_back(t->GetV1()[iEntry], t->GetV2()[iEntry]);
}

void
SSFitter::scaleSignalCR(TTree* t, char const* expr, char const* sel)
{
  std::cout << "Taking unbinned input for signal CR template from " << expr << " (" << sel << ")" << std::endl;

  signalCREvents_.clear();

  t->SetEstimate(t->GetEntries() + 1);
  long nEntries(t->Draw(TString::Format("%s:weight", expr), sel, "goff"));
  for (long iEntry(0); iEntry < nEntries; ++iEntry)
    signalCREvents_.emplace_back(t->GetV1()[iEntry], t->GetV2()[iEntry]);
}

void
SSFitter::fit()
{
  int nParam(1);
  if (!signalEvents_.empty())
    nParam = 3;

  TVirtualFitter* fitter(TVirtualFitter::Fitter(0, nParam));
  fitter->Clear();
  fitter->SetFCN(SSFitter::FCN);

  double verbosity(1.);
  fitter->ExecuteCommand("SET PRINT", &verbosity, 1);
  fitter->ExecuteCommand("SET WAR", 0, 0);

  fitter->SetParameter(0, "fsig", 0.9, 0.01, 0., 1.);
  if (!signalEvents_.empty()) {
    fitter->SetParameter(1, "a0", 0.001, 0.0001, 0., 0.1);
    fitter->SetParameter(2, "a1", 0.9, 0.01, 0.5, 1.1);
  }

  // normalize templates
  target_->Scale(1. / target_->GetSumOfWeights());
  signalTemplate_->Scale(1. / signalTemplate_->GetSumOfWeights());
  bkgTemplate_->Scale(1. / bkgTemplate_->GetSumOfWeights());
  signalCRTemplate_->Scale(1. / signalCRTemplate_->GetSumOfWeights());

  double errdef(1.);
  fitter->ExecuteCommand("SET ERRDEF", &errdef, 1);

  int status(fitter->ExecuteCommand("MINIMIZE", 0, 0));

  std::cout << "status " << status << std::endl;

  if (status == 0) {
    char name[100];
    double error;
    double vlow;
    double vhigh;

    fitter->GetParameter(0, name, fsig_, error, vlow, vhigh);

    double nsig(nTarg_ * fsig_);
    double nbkg(nTarg_ - nsig);

    target_->Scale(nTarg_);
    bkgTemplate_->Scale(nbkg / (1. - ROverB_ * nsig));

    if (!signalEvents_.empty()) {
      double a0;
      double a1;
      fitter->GetParameter(1, name, a0, error, vlow, vhigh);
      fitter->GetParameter(2, name, a1, error, vlow, vhigh);

      refillSignalTemplate(a0, a1);

      if (!signalCREvents_.empty())
        refillSignalCRTemplate(a0, a1);
    }

    signalTemplate_->Scale(nsig);
    signalCRTemplate_->Scale(nbkg * ROverB_ * nsig / (1. - ROverB_ * nsig));

    std::cout << "Normalized background template to " << nbkg / (1. - ROverB_ * nsig) << std::endl;
    std::cout << "Normalized signal template to " << nsig << std::endl;
    std::cout << "Normalized signalCR template to " << ROverB_ * nsig * nbkg / (1. - ROverB_ * nsig) << std::endl;
  }
}

double
SSFitter::fcn(double* _xval)
{
  if (!signalEvents_.empty()) {
    refillSignalTemplate(_xval[1], _xval[2]);
    if (!signalCREvents_.empty())
      refillSignalCRTemplate(_xval[1], _xval[2]);
  }

  double p(_xval[0]);
  double nsigRB(nTarg_ * p * ROverB_);
  double bkgnorm(1. / (1. - nsigRB));

  double chi2(0.);

  for (int iX(1); iX <= target_->GetNbinsX(); ++iX) {
    double denom(target_->GetBinError(iX));
    if (denom == 0.)
      denom = 1.;

    double diff(target_->GetBinContent(iX));
    diff -= p * signalTemplate_->GetBinContent(iX);
    diff -= (1. - p) * (bkgTemplate_->GetBinContent(iX) - nsigRB * signalCRTemplate_->GetBinContent(iX)) * bkgnorm;

    chi2 += diff * diff / denom / denom;
  }

  return chi2;
}

double
SSFitter::getPurity(int cutBin) const
{
  double nsig(getNsig(cutBin));
  double nbkg(getNbkg(cutBin));
  return nsig / (nsig + nbkg);
}

double
SSFitter::getNsig(int cutBin) const
{
  return signalTemplate_->Integral(1, cutBin);
}

double
SSFitter::getNbkg(int cutBin) const
{
  return bkgTemplate_->Integral(1, cutBin) - signalCRTemplate_->Integral(1, cutBin);
}

void
SSFitter::preparePlot()
{
  delete total_;
  delete subtractedBkg_;

  bkgTemplate_->SetLineColor(kMagenta);
  bkgTemplate_->SetLineWidth(2);
  bkgTemplate_->SetLineStyle(kDashed);

  gROOT->cd("SSFitter");
  subtractedBkg_ = (TH1*)bkgTemplate_->Clone("subtracted");
  subtractedBkg_->Add(signalCRTemplate_, -1.);
  subtractedBkg_->SetLineColor(kGreen);
  subtractedBkg_->SetLineWidth(2);
  subtractedBkg_->SetLineStyle(kDashed);

  signalTemplate_->SetLineColor(kRed);
  signalTemplate_->SetLineWidth(2);
  signalTemplate_->SetLineStyle(kDashed);

  total_ = (TH1*)signalTemplate_->Clone("signal");
  total_->Add(subtractedBkg_);
  total_->SetLineColor(kBlue);
  total_->SetLineWidth(2);
  total_->SetLineStyle(kSolid);

  target_->SetMarkerStyle(8);
  target_->SetMarkerColor(kBlack);
  target_->SetLineColor(kBlack);
}

void
SSFitter::plotOn(TCanvas* _canvas)
{
  SSFitter::preparePlot();

  _canvas->cd();
  total_->Draw("HIST");
  signalTemplate_->Draw("HIST SAME");
  bkgTemplate_->Draw("HIST SAME");
  subtractedBkg_->Draw("HIST SAME");
  target_->Draw("EP SAME");
}

void
SSFitter::refillSignalTemplate(double a0, double a1)
{
  signalTemplate_->Reset();
  for (unsigned iS(0); iS != signalEvents_.size(); ++iS)
    signalTemplate_->Fill(a0 + a1 * signalEvents_[iS].first, signalEvents_[iS].second);

  signalTemplate_->Scale(1. / signalTemplate_->GetSumOfWeights());
}

void
SSFitter::refillSignalCRTemplate(double a0, double a1)
{
  signalCRTemplate_->Reset();
  for (unsigned iS(0); iS != signalCREvents_.size(); ++iS)
    signalCRTemplate_->Fill(a0 + a1 * signalCREvents_[iS].first, signalCREvents_[iS].second);

  signalCRTemplate_->Scale(1. / signalCRTemplate_->GetSumOfWeights());
}

/*static*/
SSFitter*
SSFitter::singleton()
{
  static SSFitter fitter;
  return &fitter;
}

/*static*/
void
SSFitter::FCN(int&, double*, double& fval, double* xval, int)
{
  fval = SSFitter::singleton()->fcn(xval);
}
