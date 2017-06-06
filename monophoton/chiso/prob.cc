#include "PandaTree/Objects/interface/EventMonophoton.h"

#include "TTree.h"
#include "TFile.h"
#include "TH1D.h"

void
pvprob(TTree* _input, TFile* _wsource, TFile* _outputFile, long _nEntries = -1)
{
  panda::EventMonophoton event;
  _input->SetBranchStatus("*", false);
  event.setAddress(*_input, {"photons", "vertices"});

  auto* tempLow(static_cast<TH1D*>(_wsource->Get("low")));
  auto* tempMed(static_cast<TH1D*>(_wsource->Get("med")));
  auto* tempHigh(static_cast<TH1D*>(_wsource->Get("high")));

  double binning[] = {175., 200., 250., 300., 500., 800.};
  _outputFile->cd();
  auto* hdenom(new TH1D("denom", ";p_{T}^{#gamma} (GeV)", sizeof(binning) / sizeof(double) - 1, binning));
  auto* hnumer(new TH1D("numer", ";p_{T}^{#gamma} (GeV)", sizeof(binning) / sizeof(double) - 1, binning));
  hdenom->Sumw2();
  hnumer->Sumw2();

  long iEntry(0);
  while (iEntry != _nEntries && event.getEntry(*_input, iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << iEntry << std::endl;

    auto& photon(event.photons[0]);

    if (photon.scRawPt < 175. || photon.nhIso > 2.725 || photon.phIso > 2.571 || photon.chIso < 1. || photon.sieie < 0.012 || photon.hOverE > 0.0396)
      continue;

    double pt(photon.scRawPt);

    TH1D* temp(0);
    if (pt < 200.)
      temp = tempLow;
    else if (pt < 250.)
      temp = tempMed;
    else
      temp = tempHigh;

    double score(std::log(event.vertices[1].score));
    int iX(temp->FindBin(score));
    double w(0.);
    if (iX == 0)
      w = 1.;
    else if (iX == temp->GetNbinsX() + 1)
      w = 0.;
    else
      w = temp->Integral(iX + 1, temp->GetNbinsX()) + temp->GetBinContent(iX) * (score - temp->GetXaxis()->GetBinLowEdge(iX)) / temp->GetXaxis()->GetBinWidth(iX);

    hdenom->Fill(pt);
    hnumer->Fill(pt, w);
  }
}
