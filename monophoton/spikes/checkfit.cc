TObjArray pulses;
TObjArray markers;
TH1F* frame = 0;

void
checkfit(TTree* tree, int entry, bool overlay = false, int color = kRed)
{
  if (!overlay) {
    gStyle->SetOptStat(0);
    if (!frame) {
      frame = new TH1F("frame", "", 1, 0., 10.);
      frame->SetMinimum(-0.05);
      frame->SetMaximum(1.1);
    }
    frame->Draw();
  }

  float sample[10];
  float amplitude;
  float alpha;
  float beta;
  float t0;
  unsigned short gainId[10];

  tree->SetBranchAddress("sample", sample);
  tree->SetBranchAddress("amplitude", &amplitude);
  tree->SetBranchAddress("alpha", &alpha);
  tree->SetBranchAddress("beta", &beta);
  tree->SetBranchAddress("t0", &t0);
  tree->SetBranchAddress("gainId", gainId);

  tree->GetEntry(entry);

  TF1* pulse = new TF1(TString::Format("pulse%d", entry), "TMath::Power(TMath::Max(0., 1. + (x - [2]) / [0] / [1]), [0]) * TMath::Exp(-(x - [2]) / [1])", 0., 10.);
  pulses.Add(pulse);
  TMarker gain12(0., 0., 20);
  TMarker gain6(0., 0., 21);
  TMarker gain1(0., 0., 22);

  gain12.SetMarkerColor(color);
  gain6.SetMarkerColor(color);
  gain1.SetMarkerColor(color);

  for (int iX = 0; iX != 10; ++iX) {
    if (gainId[iX] == 1)
      gain12.DrawMarker(iX, sample[iX] / amplitude);
    else if (gainId[iX] == 2)
      gain6.DrawMarker(iX, sample[iX] / amplitude);
    else if (gainId[iX] == 3)
      gain1.DrawMarker(iX, sample[iX] / amplitude);
  }

  std::cout << " h = " << amplitude;
  std::cout << " alpha = " << alpha;
  std::cout << " beta = " << beta;
  std::cout << " t0 = " << t0;
  std::cout << std::endl;

  pulse->SetParameters(alpha, beta, t0);

  pulse->SetLineColor(color);

  pulse->Draw("SAME");
}
