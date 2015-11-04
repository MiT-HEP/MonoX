void trig_updated(){

    TStyle *tdrStyle = new TStyle("tdrStyle","Style for P-TDR");

    // For the canvas:
    tdrStyle->SetCanvasBorderMode(0);
    tdrStyle->SetCanvasColor(kWhite);
    tdrStyle->SetCanvasDefH(600); //Height of canvas
    tdrStyle->SetCanvasDefW(600); //Width of canvas
    tdrStyle->SetCanvasDefX(0);   //POsition on screen
    tdrStyle->SetCanvasDefY(0);

    // For the Pad:
    tdrStyle->SetPadBorderMode(0);
    tdrStyle->SetPadColor(kWhite);
    tdrStyle->SetPadGridX(true);
    tdrStyle->SetPadGridY(true);
    tdrStyle->SetGridColor(0);
    tdrStyle->SetGridStyle(3);
    tdrStyle->SetGridWidth(1);

    // For the frame:
    tdrStyle->SetFrameBorderMode(0);
    tdrStyle->SetFrameBorderSize(1);
    tdrStyle->SetFrameFillColor(0);
    tdrStyle->SetFrameFillStyle(0);
    tdrStyle->SetFrameLineColor(1);
    tdrStyle->SetFrameLineStyle(1);
    tdrStyle->SetFrameLineWidth(1);

    // For the histo:
    tdrStyle->SetHistLineColor(1);
    tdrStyle->SetHistLineStyle(0);
    tdrStyle->SetHistLineWidth(1);

    tdrStyle->SetEndErrorSize(2);
    tdrStyle->SetErrorX(0.);

    tdrStyle->SetMarkerStyle(20);

    //For the fit/function:
    tdrStyle->SetOptFit(0);
    tdrStyle->SetFitFormat("5.4g");
    tdrStyle->SetFuncColor(2);
    tdrStyle->SetFuncStyle(1);
    tdrStyle->SetFuncWidth(1);

    //For the date:
    tdrStyle->SetOptDate(0);

    // For the statistics box:
    tdrStyle->SetOptFile(0);
    //tdrStyle->SetOptStat("emr"); // To display the mean and RMS:   SetOptStat("mr");
    tdrStyle->SetOptStat(0); // To display the mean and RMS:   SetOptStat("mr");
    tdrStyle->SetStatColor(kWhite);
    tdrStyle->SetStatFont(42);
    tdrStyle->SetStatFontSize(0.025);
    tdrStyle->SetStatTextColor(1);
    tdrStyle->SetStatFormat("6.4g");
    tdrStyle->SetStatBorderSize(1);
    tdrStyle->SetStatH(0.1);
    tdrStyle->SetStatW(0.15);

    // Margins:
    tdrStyle->SetPadTopMargin(0.07);
    tdrStyle->SetPadBottomMargin(0.13);
    tdrStyle->SetPadLeftMargin(0.13);
    tdrStyle->SetPadRightMargin(0.05);

    // For the Global title:
    tdrStyle->SetTitleFont(35);
    tdrStyle->SetTitleColor(1);
    tdrStyle->SetTitleTextColor(1);
    tdrStyle->SetTitleFillColor(10);
    tdrStyle->SetTitleFontSize(0.045);
    tdrStyle->SetTitleX(0.15); // Set the position of the title box
    tdrStyle->SetTitleBorderSize(0);

    // For the axis titles:
    tdrStyle->SetTitleColor(1, "XYZ");
    tdrStyle->SetTitleFont(42, "XYZ");
    tdrStyle->SetTitleSize(0.04, "XYZ");
    tdrStyle->SetTitleXOffset(0.9);
    tdrStyle->SetTitleYOffset(1.05);

    // For the axis labels:
    tdrStyle->SetLabelColor(1, "XYZ");
    tdrStyle->SetLabelFont(42, "XYZ");
    tdrStyle->SetLabelOffset(0.007, "XYZ");
    tdrStyle->SetLabelSize(0.03, "XYZ");

    // For the axis:
    tdrStyle->SetAxisColor(1, "XYZ");
    tdrStyle->SetStripDecimals(kTRUE);
    tdrStyle->SetTickLength(0.03, "XYZ");
    tdrStyle->SetNdivisions(510, "XYZ");
    tdrStyle->SetPadTickX(1);  // To get tick marks on the opposite side of the frame
    tdrStyle->SetPadTickY(1);

    // Change for log plots:
    tdrStyle->SetOptLogx(0);
    tdrStyle->SetOptLogy(0);
    tdrStyle->SetOptLogz(0);

    // Postscript options:
    tdrStyle->SetPaperSize(20.,20.);
    tdrStyle->SetPalette(1);

    gROOT -> ForceStyle();

    tdrStyle->cd();

    TString directory = "eos/cms/store/user/zdemirag/FrozenMonoJet/";
    TString directory_data = "eos/cms/store/user/zdemirag/FrozenMonoJet/";
    //TString directory = "eos/cms/store/user/zdemirag/FrozenMonoJetSlim/";
    //TString directory_data = "eos/cms/store/user/zdemirag/FrozenMonoJetSlim/";

    TFile *f = new TFile(directory+"monojet_WJetsToLNu.root","READ");
    const Int_t nbins = 16;
    const Int_t npoints = nbins+1;
    double ptbins[npoints] = {50,60,70,80,90,100,125,150,175,200,250,300,350,400,500,600,1000};

    TH1F *den_mc_met = new TH1F("den_mc_met","den_mc_met",16,ptbins);
    TH1F *num_mc_met = new TH1F("num_mc_met","num_mc_met",16,ptbins);
    eff_mc_met= new TGraphAsymmErrors;
    den_mc_met->Sumw2();
    num_mc_met->Sumw2();

    TString name = "met";
    
    TString offline = "jet1Pt>100. && TMath::Abs(jet1Eta)<2.5 && jet1isMonoJetId==1 && n_tightlep > 0 && n_looselep>0 && abs(minJetMetDPhi)>0.5";

    TString cut_den = "(triggerFired[5] || triggerFired[6]) && "+offline;
    TString cut_num = "(triggerFired[5] || triggerFired[6]) && (triggerFired[1] || triggerFired[0] || triggerFired[2]) && "+offline;

    events->Draw(name+">>den_mc_met",cut_den,"");
    events->Draw(name+">>num_mc_met",cut_num,"");

    TFile *f2 = new TFile(directory_data+"monojet_SingleMuon+Run2015D.root","READ");
    
    TH1F *den_data_met = new TH1F("den_data_met","den_data_met",nbins,ptbins);
    TH1F *num_data_met = new TH1F("num_data_met","num_data_met",nbins,ptbins);
    eff_data_met= new TGraphAsymmErrors;
    den_data_met->Sumw2();
    num_data_met->Sumw2();

    events->Draw(name+">>den_data_met",cut_den,"");
    events->Draw(name+">>num_data_met",cut_num,"");

    TCanvas *c1 = new TCanvas("c1","c1",1000,800);
    c1->SetBottomMargin(0.35);
    c1->SetRightMargin(0.04);
    c1->SetTopMargin(0.07);
    c1->SetLeftMargin(0.18);
    c1->cd();

    TH1F *dummy = new TH1F("dummy","",1,ptbins[0],ptbins[nbins]);
    dummy->SetBinContent(1,0.0);
    dummy->SetLineColor(0);
    dummy->SetMarkerColor(0);
    dummy->SetLineWidth(0);
    dummy->SetMarkerSize(0);
    dummy->GetYaxis()->SetTitle("Efficiency");
    dummy->GetXaxis()->SetTitle("");
    dummy->GetXaxis()->SetTitleSize(0);
    dummy->GetXaxis()->SetLabelSize(0);
    dummy->SetMinimum(0.01);
    dummy->SetMaximum(1.19);
    dummy->Draw("hist");

    eff_mc_met->BayesDivide(num_mc_met,den_mc_met,"");
    eff_mc_met->SetLineColor(2);
    eff_mc_met->SetMarkerColor(2);
    eff_mc_met->SetMarkerStyle(20);
    eff_mc_met->SetMarkerSize(1.2);
    eff_mc_met->Draw("psame");

    TF1 *f1 = new TF1("f1","1",0,1000);
    f1->SetLineColor(kGreen+2);
    f1->SetLineStyle(2);
    f1->SetLineWidth(2);
    f1->Draw("same");

    //TF1 *erf1 = new TF1("erf1", "0.5*[2]*(1+TMath::Erf( (x-[0]) / ([1]*sqrt(2)) ) )",0.0,1000.0);
    TF1 *erf1 = new TF1("erf1", ErfCB,0.0,1000.0,5);
    erf1->SetParameter(0,100);
    erf1->SetParameter(1,2);
    erf1->SetParameter(2,0.5);
    erf1->SetParameter(3,3);
    erf1->SetParameter(4,0.9);
    //erf1->SetParLimits(2,0.0,1.0);
    erf1->SetLineColor(2);
    erf1->SetLineWidth(2);
    eff_mc_met->Fit("erf1","RMB");

    eff_data_met->BayesDivide(num_data_met,den_data_met,"");
    eff_data_met->SetLineColor(4);
    eff_data_met->SetMarkerColor(4);
    eff_data_met->SetMarkerStyle(20);
    eff_data_met->SetMarkerSize(1.2);
    eff_data_met->Draw("psame");

    TF1 *erf2 = new TF1("erf2", ErfCB,0.0,1000.0,5);
    erf2->SetParameter(0,100);
    erf2->SetParameter(1,2);
    erf2->SetParameter(2,0.5);
    erf2->SetParameter(3,3);
    erf2->SetParameter(4,0.9);
    //erf2->SetParLimits(2,0.0,1.0);
    erf2->SetLineColor(4);
    erf2->SetLineWidth(2);
    eff_data_met->Fit("erf2","RMBsame");

    TLatex *latex1 = new TLatex;
    latex1->SetNDC();
    latex1->SetTextSize(0.025);
    latex1->SetTextAlign(31);
    latex1->SetTextSize(0.5*c1->GetTopMargin());
    latex1->SetTextFont(42);
    latex1->DrawLatex(0.9, 0.94,"209 pb^{-1} (13 TeV)");
    latex1->SetTextSize(0.8*c1->GetTopMargin());                              
    latex1->SetTextFont(62);                               
    latex1->SetTextAlign(11);
    latex1->DrawLatex(0.20, 0.86, "CMS");
    latex1->SetTextSize(0.7*c1->GetTopMargin());                                    
    latex1->SetTextFont(52);                               
    latex1->SetTextAlign(11);                                                      
    latex1->DrawLatex(0.30, 0.86, "Preliminary");                                  


    TPad *pad = new TPad("pad", "pad", 0.0, 0.0, 1.0, 1.0);
    pad->SetTopMargin(0.65);
    pad->SetRightMargin(0.04);
    pad->SetLeftMargin(0.18);
    pad->SetFillColor(0);
    pad->SetGridy(1);
    pad->SetFillStyle(0);
    pad->Draw();
    pad->cd(0);
    
    TH1F *dummy2 = new TH1F("dummy2","",1,ptbins[0],ptbins[nbins]);
    dummy2->SetBinContent(1,0.0);
    dummy2->SetLineColor(0);
    dummy2->SetMarkerColor(0);
    dummy2->SetLineWidth(0);
    dummy2->SetMarkerSize(0);
    dummy2->GetYaxis()->SetLabelSize(0.02);
    dummy2->GetYaxis()->SetTitle("Data / MC");
    dummy2->GetXaxis()->SetTitle("U [GeV]");
    dummy2->GetYaxis()->SetNdivisions(10);
    dummy2->GetXaxis()->SetNdivisions(510);
    dummy2->GetYaxis()->CenterTitle();
    dummy2->SetMinimum(0.9);
    dummy2->SetMaximum(1.09);
    dummy2->Draw("hist");

    Double_t met[nbins]; Double_t dmet[nbins];
    Double_t ratio[nbins]; Double_t ratio_hi[nbins]; Double_t ratio_lo[nbins];
    for (int i=0; i<=nbins; i++) {
        met[i]=ptbins[i]+0.5*(ptbins[i+1]-ptbins[i]);
        dmet[i]=0.5*(ptbins[i+1]-ptbins[i]);
        ratio[i]=eff_data_met->GetY()[i]/eff_mc_met->GetY()[i];
        ratio_hi[i]=ratio[i]*sqrt((eff_data_met->GetEYhigh()[i]/eff_data_met->GetY()[i])**2+(eff_mc_met->GetEYhigh()[i]/eff_mc_met->GetY()[i])**2);
        ratio_lo[i]=ratio[i]*sqrt((eff_data_met->GetEYlow()[i]/eff_data_met->GetY()[i])**2+(eff_mc_met->GetEYlow()[i]/eff_mc_met->GetY()[i])**2);
    }

    ratio_datamc_met = new TGraphAsymmErrors(nbins,met,ratio,dmet,dmet,ratio_lo,ratio_hi);
    ratio_datamc_met->SetTitle("");
    ratio_datamc_met->SetMarkerColor(1);
    ratio_datamc_met->SetMarkerSize(1.2);
    ratio_datamc_met->SetMarkerStyle(20);
    ratio_datamc_met->Draw("psame");

    gPad->RedrawAxis();

    c1->SaveAs("/afs/cern.ch/user/z/zdemirag/www/Monojet/frozen/signal/trigeff.pdf");
    c1->SaveAs("/afs/cern.ch/user/z/zdemirag/www/Monojet/frozen/signal/trigeff.png");
    c1->SaveAs("/afs/cern.ch/user/z/zdemirag/www/Monojet/frozen/signal/trigeff.C");

}

Double_t ErfCB(double *x, double *par)
{ 
    double m = x[0];
    double m0 = par[0];
    double sigma = par[1];
    double alpha = par[2];
    double n = par[3];
    double norm = par[4];
  
    const double sqrtPiOver2 = 1.2533141373; // sqrt(pi/2)
    const double sqrt2 = 1.4142135624;

    Double_t sig = fabs((Double_t) sigma);
    Double_t t = (m - m0)/sig ;
  
    if (alpha < 0)
        t = -t;

    Double_t absAlpha = fabs(alpha / sig);
    Double_t a = TMath::Power(n/absAlpha,n)*exp(-0.5*absAlpha*absAlpha);
    Double_t b = absAlpha - n/absAlpha;

    Double_t leftArea = (1 + ApproxErf( absAlpha / sqrt2 )) * sqrtPiOver2 ;
    Double_t rightArea = ( a * 1/TMath::Power(absAlpha - b,n-1)) / (n - 1);
    Double_t area = leftArea + rightArea ;

    if ( t <= absAlpha ){
        return norm * (1 + ApproxErf( t / sqrt2 )) * sqrtPiOver2 / area ;
    }
    else{
        return norm * (leftArea +  a * (1/TMath::Power(t-b,n-1) - 1/TMath::Power(absAlpha - b,n-1)) / (1 - n)) / area ;
    }
  
} 

Double_t ApproxErf(Double_t arg)
{
    static const double erflim = 5.0;
    if( arg > erflim )
        return 1.0;
    if( arg < -erflim )
        return -1.0;
  
    return TMath::Erf(arg);
}
    
    
    
