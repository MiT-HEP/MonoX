from ROOT import *
from collections import defaultdict

from array import array
from tdrStyle import *
setTDRStyle()

blind = False

new_dic = defaultdict(dict)

def plotPreFitPostFit(region,category,sb=False):

  datalab = {"monomu":"monomu", "dimu":"dimu", "monophLowPhi":"monophLowPhi", "monophHighPhi":"monophHighPhi", "monoel":"monoel", "diel":"diel", "dilep":"dilep", "monolep":"monolep"}
  
  f_mlfit = TFile('mlfit.root','READ')

  f_data = TFile('/data/t3home000/ballen/monophoton/fit/ws_phoPtHighMet_plots.root')
  # ws = f_data.Get('wspace')

  n_data = 'data_obs_' + region + '__x'
  print n_data
  h_data = f_data.Get(n_data)
  print h_data

  h_postfit_sig = f_mlfit.Get("shapes_fit_b/" + region + "/total_background")
  h_prefit_sig = f_mlfit.Get("shapes_prefit/" + region + "/total_background")
  
  b_width = [50,50,50,50,100,100,300,400,0]

  channel = {"monomu":"monomu", "dimu":"dimu", "monophHighPhi":"monophHighPhi", "monophLowPhi":"monophLowPhi", "monoel":"monoel", "diel":"diel", "dilep":"dilep", "monolep":"monolep"}
  mainbkg = {"monomu":"wg", "dimu":"zg", "monophHighPhi":"zg", "monophLowPhi":"zg", "monoel":"wg", "diel":"zg", "monolep":"wg", "dilep":"zg"}
  

  processes = [
    'zjets',
    'gg',
    'minor',
    'wjets',
    'vvg',
    'top',
    'spike',
    'halo',
    'gjets',
    'hfake',
    'efake',
    'wg',
    'zg'
    ]


 
  colors = {
    'zg'     :"#99ffaa",
    'wg'     :"#99eeff",
    'efake'  :"#ffee99",
    'hfake'  :"#bbaaff",
    'halo'   :"#ff9933",
    'spike'  :"#666666",
    'vvg'    :"#ff4499",
    'gjets'  :"#ffaacc",
    'minor'  :"#bb66ff",
    'top'    :"#5544ff",
    'zjets'  :"#99ffaa",
    'wjets'  :"#222222",
    'gg'     :"#bb66ff"
  }

  binLowE = []

  # Pre-Fit
  h_prefit = {}
  #h_prefit['total'] = f_mlfit.Get("shapes_prefit/ch"+channel[region]+"/total")
  print f_mlfit
  h_prefit['total'] = f_mlfit.Get("shapes_prefit/"+channel[region]+"/total")
  print h_prefit['total']
  print "shapes_prefit/"+channel[region]+"/total"
  for i in range(1,h_prefit['total'].GetNbinsX()+2):
    binLowE.append(h_prefit['total'].GetBinLowEdge(i))

  h_all_prefit = TH1F("h_all_prefit","h_all_prefit",len(binLowE)-1,array('d',binLowE))    
  h_other_prefit = TH1F("h_other_prefit","h_other_prefit",len(binLowE)-1,array('d',binLowE))    
  h_stack_prefit = THStack("h_stack_prefit","h_stack_prefit")    

  for process in processes:
    #h_prefit[process] = f_mlfit.Get("shapes_prefit/ch"+channel[region]+"/"+process)
    h_prefit[process] = f_mlfit.Get("shapes_prefit/"+channel[region]+"/"+process)
    if (not h_prefit[process]): continue
    if (str(h_prefit[process].Integral())=="nan"): continue
    for i in range(1,h_prefit[process].GetNbinsX()+1):
      content = h_prefit[process].GetBinContent(i)
      width = h_prefit[process].GetBinLowEdge(i+1)-h_prefit[process].GetBinLowEdge(i)
      h_prefit[process].SetBinContent(i,content*width)
    #print "Pre-Fit",process,h_prefit[process].Integral()
    #h_prefit[process].SetLineColor(colors[process])
    #h_prefit[process].SetFillColor(colors[process])
    h_prefit[process].SetLineColor(TColor.GetColor(colors[process]))
    h_prefit[process].SetFillColor(TColor.GetColor(colors[process]))
    h_all_prefit.Add(h_prefit[process])
    if (not process==mainbkg[region]): 
      h_other_prefit.Add(h_prefit[process])
    h_stack_prefit.Add(h_prefit[process])
    

  # Post-Fit
  h_postfit = {}
  h_postfit['totalsig'] = f_mlfit.Get("shapes_fit_s/"+channel[region]+"/total")
  #h_postfit['total'] = f_mlfit.Get("shapes_fit_b/ch"+channel[region]+"/total")
  h_postfit['total'] = f_mlfit.Get("shapes_fit_b/"+channel[region]+"/total")
  h_all_postfit = TH1F("h_all_postfit","h_all_postfit",len(binLowE)-1,array('d',binLowE))    
  h_other_postfit = TH1F("h_other_postfit","h_other_postfit",len(binLowE)-1,array('d',binLowE))    
  h_minor_postfit = TH1F("h_minor_postfit","h_minor_postfit",len(binLowE)-1,array('d',binLowE))

  h_stack_postfit = THStack("h_stack_postfit","h_stack_postfit")    
  

  #h_postfit['totalv2'] = f_mlfit.Get("shapes_fit_s/ch"+channel[region]+"/total_background")
  #h_postfit['totalv2'] = f_mlfit.Get("shapes_fit_b/ch"+channel[region]+"/total_background")
  h_postfit['totalv2'] = f_mlfit.Get("shapes_fit_b/"+channel[region]+"/total_background")

  for i in range(1, h_postfit['totalv2'].GetNbinsX()+1):
    error = h_postfit['totalv2'].GetBinError(i)
    content = h_postfit['totalv2'].GetBinContent(i)
    #print 'TOTAL',i, content, error, error/content*100

  for process in processes:
    print "\n\n",process
    #h_postfit[process] = f_mlfit.Get("shapes_fit_s/ch"+channel[region]+"/"+process)
    #h_postfit[process] = f_mlfit.Get("shapes_fit_b/ch"+channel[region]+"/"+process)
    h_postfit[process] = f_mlfit.Get("shapes_fit_b/"+channel[region]+"/"+process)
    print h_postfit[process]
    if (not h_postfit[process]): continue
    if (str(h_postfit[process].Integral())=="nan"): continue
    for i in range(1,h_postfit[process].GetNbinsX()+1):
      error = h_postfit[process].GetBinError(i)
      content = h_postfit[process].GetBinContent(i)
      width = h_postfit[process].GetBinLowEdge(i+1)-h_postfit[process].GetBinLowEdge(i)
      h_postfit[process].SetBinContent(i,content*width)
      #new_dic[process][i] = content
      #print "Post-Fit",i,process,content,
      #print "$"+str(round(content,2))+"$        " , " & ",

    h_postfit[process].SetLineColor(1)
    h_postfit[process].SetFillColor(TColor.GetColor(colors[process]))
    h_all_postfit.Add(h_postfit[process])
    if (not process==mainbkg[region]):
      h_other_postfit.Add(h_postfit[process])
    h_postfit[process].Scale(1,"width")    

    h_stack_postfit.Add(h_postfit[process])
      
  #print "\n\n POSTFIT YIELDS"
  h_all_postfit.Scale(1,"width")

  #for i in range(1,h_all_postfit.GetNbinsX()+1):
    #print "$"+str(round(h_all_postfit.GetBinContent(i),2))+"$        " , " & ",
    #print "$"+str(round(h_all_postfit.GetBinError(i),4))+"$        " , " & ",

  #print "\n\n PREFIT YIELDS"
  h_all_prefit.Scale(1,"width")

  #for i in range(1,h_all_prefit.GetNbinsX()+1):
    #print "$"+str(round(h_all_prefit.GetBinContent(i),2))+"$        " , " & ",
           
  gStyle.SetOptStat(0)

  #latex2 = TLatex()
  #latex2.SetNDC()
  #latex2.SetTextSize(0.5*c.GetTopMargin())
  #latex2.SetTextFont(42)
  #latex2.SetTextAlign(31) # align right
  #latex2.DrawLatex(0.9, 0.94,"209 pb^{-1} (13 TeV)")
  ##latex2.SetTextSize(0.8*c.GetTopMargin())
  #latex2.SetTextFont(62)
  #latex2.SetTextAlign(11) # align right
  #latex2.DrawLatex(0.19, 0.85, "CMS")
  ##latex2.SetTextSize(0.7*c.GetTopMargin())
  #latex2.SetTextFont(52)
  #latex2.SetTextAlign(11)
  #latex2.DrawLatex(0.28, 0.85, "Preliminary")          

  #0.1 x 0.3 - 1 y
  # 0.029, 0.35

  c = TCanvas("c","c",600,700)  
  SetOwnership(c,False)
  c.cd()
  c.SetLogy()
  c.SetBottomMargin(0.3)
  c.SetRightMargin(0.06)
  c.SetTickx(1);
  c.SetTicky(1);
  #c.SetTopMargin(0.07)
  #c.SetLeftMargin(0.18)
  
  dummy = h_all_prefit.Clone("dummy")
  #dummy = TH1F("dummy","dummy",len(binLowE)-1,array('d',binLowE))
  #for i in range(1,dummy.GetNbinsX()):
  #  dummy.SetBinContent(i,0.01)
  dummy.SetFillColor(0)
  dummy.SetLineColor(0)
  dummy.SetLineWidth(0)
  dummy.SetMarkerSize(0)
  dummy.SetMarkerColor(0) 
  dummy.GetYaxis().SetTitle("Events / GeV")
  dummy.GetXaxis().SetTitle("")
  dummy.GetXaxis().SetTitleSize(0)
  dummy.GetXaxis().SetLabelSize(0)
  dummy.SetMaximum(25*dummy.GetMaximum())
  #dummy.SetMaximum(dummy.GetMaximum())
  dummy.SetMinimum(0.002)
  dummy.GetYaxis().SetTitleOffset(1.15)
  dummy.Draw()
  

  h_other_prefit.SetLineColor(1)
  #h_other_prefit.SetFillColor(kOrange+1)
  h_other_prefit.SetFillColor(kGray)
  #h_other_prefit.SetFillColor(kGray)
  h_other_prefit.Scale(1,"width")

  #h_stack_prefit.Scale(1,"width")
  #h_stack_prefit.Draw("histsame")

  h_all_prefit.SetLineColor(2)
  h_all_prefit.SetLineWidth(2)

  h_all_postfit.SetLineColor(4)
  h_all_postfit.SetLineWidth(2)

  if region in ['monophLowPhi', 'monophHighPhi']:

    h_postfit['totalsig'].SetLineColor(1);
    h_postfit['totalsig'].SetFillColor(1);
    h_postfit['totalsig'].SetFillStyle(3144);
    if sb:
      h_postfit['totalsig'].Draw("samehist")

    h_stack_postfit.Draw("histsame")
    


  else:    
    h_other_prefit.Draw("histsame")
    h_all_prefit.SetLineStyle(7)
    h_all_prefit.Draw("histsame")
    h_all_postfit.Draw("histsame")



  h_data.SetMarkerStyle(20)
  h_data.SetMarkerSize(1.2)
  h_data.Scale(1,"width")
  if not blind:
    h_data.Draw("epsame")

  #print "\n\n DATA"
  #for i in range(1,h_data.GetNbinsX()+1):
    #print "$"+str(round(h_data.GetBinContent(i),2))+"$        " , " & ",


  if region == "monomu":
    #legname = "W #rightarrow #mu#nu"
    legname = "single-muon C.R."
  if region == "dimu":
    #legname = "Z #rightarrow #mu#mu"
    legname = "di-muon C.R."
  if region == "gjets":
    legname = "#gamma + jets C.R."
  if region == "monoel":
    #legname = "W #rightarrow e#nu"
    legname = "single-electron C.R."
  if region == "diel":
    #legname = "Z #rightarrow ee"
    legname = "di-electron C.R."
  if region == "dilep":
    legname = "di-lepton C.R."
  if region == "monolep":
    legname = "single-lepton C.R."

  
  #legend.SetTextSize(0.04)
  if region in ['monophHighPhi', 'monophLowPhi'] :
    legend = TLegend(.625,.55,.925,.90)
    legend.AddEntry(h_data, "Data", "elp")    
    legend.AddEntry(h_postfit['zg'], "Z #rightarrow #nu#nu + #gamma", "f")
    legend.AddEntry(h_postfit['wg'], "W #rightarrow l#nu + #gamma", "f")
    legend.AddEntry(h_postfit['efake'], "Electron fakes", "f")
    legend.AddEntry(h_postfit['hfake'], "Hadron fakes", "f")
    legend.AddEntry(h_postfit['gjets'], "#gamma+jets", "f")
    legend.AddEntry(h_postfit['halo'], "Beam halo", "f")
    legend.AddEntry(h_postfit['spike'], "Spikes", "f")
    legend.AddEntry(h_postfit['top'], "t#bar{t}#gamma/t#gamma", "f")
    legend.AddEntry(h_postfit['vvg'], "VV#gamma", "f")
    legend.AddEntry(h_postfit['wjets'], "W(#mu,#tau) + jets", "f")
    legend.AddEntry(h_postfit['minor'], "Minor SM", "f")
    # legend.AddEntry(h_all_postfit, "Expected (post-fit)", "l")
    # legend.AddEntry(h_all_prefit, "Expected (pre-fit) ", "l")
    if sb:
      legend.AddEntry(h_postfit['totalsig'], "S+B post-fit", "f")

  else:
    legend = TLegend(.625,.65,.925,.90)
    #legend = TLegend(.6,.6,.92,.92)
    legend.AddEntry(h_data,"Data","elp")
    legend.AddEntry(h_all_postfit, "Post-fit "+legname, "l")
    legend.AddEntry(h_all_prefit, "Pre-fit "+legname, "l")
    legend.AddEntry(h_other_prefit, "Other Backgrounds", "f")    

  legend.SetShadowColor(0);
  legend.SetFillColor(0);
  legend.SetLineColor(0);
  legend.Draw("same")

  latex2 = TLatex()
  latex2.SetNDC()
  latex2.SetTextSize(0.6*c.GetTopMargin())
  latex2.SetTextFont(42)
  latex2.SetTextAlign(31) # align right
  #latex2.DrawLatex(0.9, 0.95,"2.77 fb^{-1} (13 TeV)")
  latex2.DrawLatex(0.94, 0.95,"35.9 fb^{-1} (13 TeV)")
  latex2.SetTextSize(0.6*c.GetTopMargin())
  latex2.SetTextFont(62)
  latex2.SetTextAlign(11) # align right
  #latex2.DrawLatex(0.19, 0.85, "CMS")
  latex2.DrawLatex(0.175, 0.85, "CMS")
  #latex2.SetTextSize(0.5*c.GetTopMargin())
  latex2.SetTextSize(0.6*c.GetTopMargin())
  latex2.SetTextFont(52)
  latex2.SetTextAlign(11)
  offset = 0.005
  latex2.DrawLatex(0.28+offset, 0.85, "Preliminary")          

  gPad.RedrawAxis()

  pad = TPad("pad", "pad", 0.0, 0.0, 1.0, 0.9)
  SetOwnership(pad,False)

  pad.SetTopMargin(0.7)
  pad.SetRightMargin(0.06)
  #pad.SetLeftMargin(0.18)
  pad.SetFillColor(0)
  pad.SetGridy(1)
  pad.SetFillStyle(0)
  pad.Draw()
  pad.cd(0)

  met = []; dmet = [];
  ratio_pre = []; ratio_pre_hi = []; ratio_pre_lo = [];
  ratio_post = []; ratio_post_hi = []; ratio_post_lo = [];

  cutstring = "("

  for i in range(1,h_all_prefit.GetNbinsX()+1):

    #ndata = array("d", [0.0])
    #metave = array("d",[0.0])
    #h_data.GetPoint(i-1, metave[0], ndata[0])

    #ndata = h_data.GetY()[i-1]
    ndata = h_data.GetBinContent(i)
    #print ndata

    if (ndata>0.0):
      e_data_hi = h_data.GetBinError(i)/ndata
      e_data_lo = h_data.GetBinError(i)/ndata
    else:
      e_data_hi = 0.0
      e_data_lo = 0.0
      

    n_all_pre = h_all_prefit.GetBinContent(i)
    n_other_pre = h_other_prefit.GetBinContent(i)
    n_all_post = h_all_postfit.GetBinContent(i)


    #n_all_pre = h_all_prefit.GetBinContent(i)
    #n_all_post = h_all_postfit.GetBinContent(i)

    
    #print h_all_prefit.GetBinLowEdge(i),h_all_prefit.GetBinLowEdge(i+1),n_all_pre,n_other_pre,n_all_post,((n_all_post-n_other_pre)/(n_all_pre-n_other_pre))
    cutstring=cutstring+str((n_all_post-n_other_pre)/(n_all_pre-n_other_pre))+"*(met>"+str(h_all_prefit.GetBinLowEdge(i))+"&&met<="+str(h_all_prefit.GetBinLowEdge(i+1))+")"
    if i<h_all_prefit.GetNbinsX():
      cutstring+="+"

    met.append(h_all_prefit.GetBinCenter(i))
    dmet.append((h_all_prefit.GetBinLowEdge(i+1)-h_all_prefit.GetBinLowEdge(i))/2)

    if (n_all_pre>0.0):
      ratio_pre.append(ndata/n_all_pre)
      ratio_pre_hi.append(ndata*e_data_hi/n_all_pre)
      ratio_pre_lo.append(ndata*e_data_lo/n_all_pre)
    else:
      ratio_pre.append(0.0)
      ratio_pre_hi.append(0.0)
      ratio_pre_lo.append(0.0)

    if (n_all_post>0.0):
      ratio_post.append(ndata/n_all_post)
      ratio_post_hi.append(ndata*e_data_hi/n_all_post)
      ratio_post_lo.append(ndata*e_data_lo/n_all_post)      
    else:
      ratio_post.append(0.0)
      ratio_post_hi.append(0.0)
      ratio_post_lo.append(0.0)

  cutstring+=")"
  #print 'cutstring for',region,cutstring

  a_met = array("d", met)
  v_met = TVectorD(len(a_met),a_met)
          
  a_dmet = array("d", dmet)
  v_dmet = TVectorD(len(a_dmet),a_dmet)
    
  a_ratio_pre = array("d", ratio_pre)
  a_ratio_pre_hi = array("d", ratio_pre_hi)
  a_ratio_pre_lo = array("d", ratio_pre_lo)
  
  v_ratio_pre = TVectorD(len(a_ratio_pre),a_ratio_pre)
  v_ratio_pre_hi = TVectorD(len(a_ratio_pre_hi),a_ratio_pre_hi)
  v_ratio_pre_lo = TVectorD(len(a_ratio_pre_lo),a_ratio_pre_lo)

  a_ratio_post = array("d", ratio_post)
  a_ratio_post_hi = array("d", ratio_post_hi)
  a_ratio_post_lo = array("d", ratio_post_lo)

  v_ratio_post = TVectorD(len(a_ratio_post),a_ratio_post)
  v_ratio_post_hi = TVectorD(len(a_ratio_post_hi),a_ratio_post_hi)
  v_ratio_post_lo = TVectorD(len(a_ratio_post_lo),a_ratio_post_lo)

  g_ratio_pre = TGraphAsymmErrors(v_met,v_ratio_pre,v_dmet,v_dmet,v_ratio_pre_lo,v_ratio_pre_hi)
  g_ratio_pre.SetLineColor(2)
  g_ratio_pre.SetMarkerColor(2)
  #g_ratio_pre.SetMarkerStyle(20)
  g_ratio_pre.SetMarkerStyle(24)

  g_ratio_post = TGraphAsymmErrors(v_met,v_ratio_post,v_dmet,v_dmet,v_ratio_post_lo,v_ratio_post_hi)
  g_ratio_post.SetLineColor(4)
  g_ratio_post.SetMarkerColor(4)
  g_ratio_post.SetMarkerStyle(20)
  
  ratiosys = h_postfit['totalv2'].Clone();
  print ratiosys
  for hbin in range(0,ratiosys.GetNbinsX()+1): 
        
    ratiosys.SetBinContent(hbin+1,1.0)
    if (h_postfit['totalv2'].GetBinContent(hbin+1)>0):
      print hbin
      print 'error', h_postfit['totalv2'].GetBinError(hbin+1)
      print 'content', h_postfit['totalv2'].GetBinContent(hbin+1)
      ratiosysbin = h_postfit['totalv2'].GetBinError(hbin+1)/h_postfit['totalv2'].GetBinContent(hbin+1)
      print ratiosysbin
      ratiosys.SetBinError(hbin+1,ratiosysbin)

      #print hbin+1, h_data.GetBinContent(hbin+1), h_postfit['totalv2'].GetBinContent(hbin+1),h_postfit['totalv2'].GetBinError(hbin+1)
      
    else:
      ratiosys.SetBinError(hbin+1,0)

    #print "Test", ratiosys.GetBinError(hbin+1)


  #dummy2 = h_all_prefit.Clone("dummy2")
  dummy2 = TH1F("dummy2","dummy2",len(binLowE)-1,array('d',binLowE))
  for i in range(1,dummy2.GetNbinsX()):
    dummy2.SetBinContent(i,1.0)
  dummy2.GetYaxis().SetTitle("Data / Pred.")
  dummy2.GetXaxis().SetTitle("E_{T}^{#gamma} [GeV]")
  dummy2.SetLineColor(0)
  dummy2.SetMarkerColor(0)
  dummy2.SetLineWidth(0)
  dummy2.SetMarkerSize(0)
  dummy2.GetYaxis().SetLabelSize(0.04)
 
  dummy2.GetYaxis().SetNdivisions(5);
  #dummy2.GetYaxis().SetNdivisions(510);
  dummy2.GetXaxis().SetNdivisions(510)
  dummy2.GetYaxis().CenterTitle()
  dummy2.GetYaxis().SetTitleSize(0.04)
  dummy2.GetYaxis().SetTitleOffset(1.5)
  #dummy2.SetMaximum(1.15*(max(v_ratio_pre)+max(v_ratio_pre_hi)))
  #if channel[region] is '2' or channel[region] is '6':
  #  dummy2.SetMaximum(1.8)
  #  dummy2.SetMinimum(0.2)
  #else:
  #  dummy2.SetMaximum(1.2)
  #  dummy2.SetMinimum(0.8)

  if region in ['monophLowPhi', 'monophHighPhi']:
    #dummy2.SetMaximum(2.4)                                                                        
    #dummy2.SetMinimum(0.1) 
    #dummy2.SetMaximum(1.85)                                                                        
    #dummy2.SetMinimum(0.15) 

    dummy2.SetMaximum(2.0)                                                                        
    dummy2.SetMinimum(0.0) 

  else:
    dummy2.SetMaximum(2.0)                                                                        
    dummy2.SetMinimum(0.0) 
    #dummy2.SetMaximum(1.85)                                                                        
    #dummy2.SetMinimum(0.15) 


  #dummy2.SetMaximum(1.5)                                                                        
  #dummy2.SetMinimum(0.5) 
  dummy2.Draw("hist")

  ratiosys.SetFillColor(kGray) #SetFillColor(ROOT.kYellow)
  ratiosys.SetLineColor(kGray) #SetLineColor(1)
  ratiosys.SetLineWidth(1)
  ratiosys.SetMarkerSize(0)
  ratiosys.Draw("e2same")

  f1 = TF1("f1","1",-5000,5000);
  f1.SetLineColor(1);
  f1.SetLineStyle(2);
  f1.SetLineWidth(2);
  f1.Draw("same")

  if not blind:
    g_ratio_pre.Draw("epsame")
    g_ratio_post.Draw("epsame")

  #legend2 = TLegend(0.15,0.26,0.46,0.25)
  #legend2 = TLegend(0.15,0.3,0.7,0.25)
  #legend2 = TLegend(0.147651,0.2314815,0.6979866,0.2810847,"","brNDC");
  legend2 = TLegend(0.14,0.24,0.40,0.27,"","brNDC")

  #legend2.AddEntry(g_ratio_post, "Background (post-fit)", "ple")
  #legend2.AddEntry(g_ratio_pre, "Background (pre-fit)", "ple")
  
  legend2.AddEntry(g_ratio_post, "post-fit", "ple")
  legend2.AddEntry(g_ratio_pre, "pre-fit", "ple")

  legend2.SetNColumns(2)

  legend2.SetShadowColor(0);  
  #legend2.SetFillStyle(0);
  legend2.SetFillColor(0);
  legend2.SetLineColor(0);
  legend2.Draw("same")

  gPad.RedrawAxis()

  folder = "/home/ballen/public_html/cmsplots/monophoton/combinedfit"
  c.SaveAs(folder+"/"+"prefit_postfit_"+region+".pdf")
  c.SaveAs(folder+"/"+"prefit_postfit_"+region+".png")
  # c.SaveAs(folder+"/"+"prefit_postfit_"+region+".C")
  # c.SaveAs(folder+"/"+"prefit_postfit_"+region+".root")


# plotPreFitPostFit("monolep","monophoton")
# plotPreFitPostFit("dilep","monophoton")

plotPreFitPostFit("monomu","monophoton")
plotPreFitPostFit("dimu","monophoton")
plotPreFitPostFit("monoel","monophoton")
plotPreFitPostFit("diel","monophoton")

plotPreFitPostFit("monophHighPhi","monophoton")
plotPreFitPostFit("monophLowPhi","monophoton")
