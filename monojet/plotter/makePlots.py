#! /usr/bin/env python
import sys, os, string, re, time, datetime
from multiprocessing import Process
from array import *

#from LoadData_ht import *
#from LoadData import *
from LoadGJets import *
#from LoadGJets_excitedquark import *
#from LoadElectron import *
#from LoadElectron_Zee import *
#from Load_Zmm import *
#from Load_Wmn import *

from ROOT import *
from math import *
from tdrStyle import *
from selection import build_selection
from datacard import dump_datacard
from pretty import plot_ratio, plot_cms

import numpy as n

vec1 = TLorentzVector()
vec2 = TLorentzVector()


setTDRStyle()

gROOT.LoadMacro("functions.C+");

metcut = 200.

print "Starting Plotting Be Patient!"

lumi = 2109.
lumi_str = 2.1

shapelimits = False
postfit = False
ht_bin = False


def plot_stack(channel, name,var, bin, low, high, ylabel, xlabel, setLog = False):

    folder = '/afs/cern.ch/user/z/zdemirag/www/Monojet/unblinding/'
    if not os.path.exists(folder):
        os.mkdir(folder)

    yield_dic = {}

    stack = THStack('a', 'a')
    if var is 'met':
        #binLowE = [200,250,300,350,400,500,600,900,1500]
        binLowE = [200,250,300,350,400,500,600,1000]
        added = TH1D('added','added',7,array('d',binLowE))
    else:
        added = TH1D('added', 'added',bin,low,high)
    added.Sumw2()
    f  = {}
    h1 = {}

    Variables = {}
    cut_standard= build_selection(channel,metcut)
    #cut_standard= build_selection(channel,200) ### Fix this back to 200 ###

    if var is 'met':
        if channel is not 'signal': 
            xlabel = 'U [GeV]'

    print "INFO Channel is: ", channel, " variable is: ", var, " Selection is: ", cut_standard,"\n"
    print 'INFO time is:', datetime.datetime.fromtimestamp( time.time())

    reordered_physics_processes = []
    if channel == 'Zmm' or channel == 'Zee': 
        reordered_physics_processes = reversed(ordered_physics_processes)
    else: 
        reordered_physics_processes = ordered_physics_processes
    #reordered_physics_processes = ordered_physics_processes

    for Type in ordered_physics_processes:
        yield_dic[physics_processes[Type]['datacard']] = 0
 
    for Type in reordered_physics_processes:
        # Create the Histograms
        histName = Type+'_'+name+'_'+channel

        if var is 'met':
            #binLowE = [200,250,300,350,400,500,600,900,1500]
            binLowE = [200,250,300,350,400,500,600,1000]
            Variables[Type] = TH1F(histName,histName,7,array('d',binLowE))
        else:
            Variables[Type] = TH1F(histName, histName, bin, low, high)

        Variables[Type].Sumw2()
        #print "\n"

        # this right now breaks the tchain logic! 
        # if we have more than 1 file, this will break!!!!  

        if Type is not 'data':
            f[Type] = ROOT.TFile(physics_processes[Type]['files'][0],"read")
            h1[Type] = f[Type].Get("htotal")
            total = h1[Type].GetBinContent(1)
            #total = h1[Type].GetEntries()
            f[Type].Close()
        else:
            total = 1.0

        input_tree   = makeTrees(Type,"events",channel)
        n_entries = input_tree.GetEntries()

        #Incase you want to apply event by event re-weighting
        #w = 1.0;

        w = "((0.0*(npv>-0.5&&npv<=0.5)+3.30418257204*(npv>0.5&&npv<=1.5)+2.59691269521*(npv>1.5&&npv<=2.5)+2.44251087681*(npv>2.5&&npv<=3.5)+2.42846225153*(npv>3.5&&npv<=4.5)+2.40062512591*(npv>4.5&&npv<=5.5)+2.30279811595*(npv>5.5&&npv<=6.5)+2.12054720297*(npv>6.5&&npv<=7.5)+1.9104708827*(npv>7.5&&npv<=8.5)+1.67904936047*(npv>8.5&&npv<=9.5)+1.43348925382*(npv>9.5&&npv<=10.5)+1.17893952713*(npv>10.5&&npv<=11.5)+0.940505177881*(npv>11.5&&npv<=12.5)+0.740901867872*(npv>12.5&&npv<=13.5)+0.56877478036*(npv>13.5&&npv<=14.5)+0.433148655714*(npv>14.5&&npv<=15.5)+0.325343558476*(npv>15.5&&npv<=16.5)+0.241688459349*(npv>16.5&&npv<=17.5)+0.180491032782*(npv>17.5&&npv<=18.5)+0.136993937378*(npv>18.5&&npv<=19.5)+0.104859480066*(npv>19.5&&npv<=20.5)+0.0768271030309*(npv>20.5&&npv<=21.5)+0.0563426184938*(npv>21.5&&npv<=22.5)+0.0454037058117*(npv>22.5&&npv<=23.5)+0.0359945616383*(npv>23.5&&npv<=24.5)+0.0286879205085*(npv>24.5&&npv<=25.5)+0.0208185595478*(npv>25.5&&npv<=26.5)+0.0170977379612*(npv>26.5&&npv<=27.5)+0.0122446391898*(npv>27.5&&npv<=28.5)+0.0148028308301*(npv>28.5&&npv<=29.5)+0.0120527550003*(npv>29.5&&npv<=30.5)+0.00402643194054*(npv>30.5&&npv<=31.5)+0.00981143754301*(npv>31.5&&npv<=32.5)+0.0*(npv>32.5&&npv<=33.5)+0.0155664899019*(npv>33.5&&npv<=34.5)+0.0*(npv>34.5&&npv<=35.5)+0.0*(npv>35.5&&npv<=36.5)+0.0*(npv>36.5&&npv<=37.5)+0.0*(npv>37.5&&npv<=38.5)+0.0*(npv>38.5&&npv<=39.5)))"

        if channel is 'signal' or channel is 'Zmm' or channel is 'Wmn':
            w_trig = '((met < 250)*0.97 + (met >=250 && met<350)* 0.987 + (met>=350)* 1.0 )'
        else:
            w_trig = '(1.0)'
            
        anlo1_over_alo = "(1.24087232993*(genBos_pt>100.0&&genBos_pt<=150.0)+1.55807026252*(genBos_pt>150.0&&genBos_pt<=200.0)+1.51043242876*(genBos_pt>200.0&&genBos_pt<=250.0)+1.47333461572*(genBos_pt>250.0&&genBos_pt<=300.0)+1.43497331471*(genBos_pt>300.0&&genBos_pt<=350.0)+1.37846354687*(genBos_pt>350.0&&genBos_pt<=400.0)+1.2920177717*(genBos_pt>400.0&&genBos_pt<=500.0)+1.31414429236*(genBos_pt>500.0&&genBos_pt<=600.0)+1.20453974747*(genBos_pt>600.0))"
        a_ewkcorr = "(0.998568444581*(genBos_pt>100.0&&genBos_pt<=150.0)+0.992098286517*(genBos_pt>150.0&&genBos_pt<=200.0)+0.986010290609*(genBos_pt>200.0&&genBos_pt<=250.0)+0.980265498435*(genBos_pt>250.0&&genBos_pt<=300.0)+0.974830448283*(genBos_pt>300.0&&genBos_pt<=350.0)+0.969676202351*(genBos_pt>350.0&&genBos_pt<=400.0)+0.962417128177*(genBos_pt>400.0&&genBos_pt<=500.0)+0.953511139209*(genBos_pt>500.0&&genBos_pt<=600.0)+0.934331895615*(genBos_pt>600.0))"

        w_ewkcorr = "(0.980859240872*(genBos_pt>100.0&&genBos_pt<=150.0)+0.962118764182*(genBos_pt>150.0&&genBos_pt<=200.0)+0.944428528597*(genBos_pt>200.0&&genBos_pt<=250.0)+0.927685912907*(genBos_pt>250.0&&genBos_pt<=300.0)+0.911802238928*(genBos_pt>300.0&&genBos_pt<=350.0)+0.896700388113*(genBos_pt>350.0&&genBos_pt<=400.0)+0.875368225896*(genBos_pt>400.0&&genBos_pt<=500.0)+0.849096933047*(genBos_pt>500.0&&genBos_pt<=600.0)+0.792158791839*(genBos_pt>600.0))"
        wnlo012_over_wlo = "(1.89123123702*(genBos_pt>100.0&&genBos_pt<=150.0)+1.70414182145*(genBos_pt>150.0&&genBos_pt<=200.0)+1.60726459197*(genBos_pt>200.0&&genBos_pt<=250.0)+1.57205818769*(genBos_pt>250.0&&genBos_pt<=300.0)+1.51688539716*(genBos_pt>300.0&&genBos_pt<=350.0)+1.41090079307*(genBos_pt>350.0&&genBos_pt<=400.0)+1.30757555038*(genBos_pt>400.0&&genBos_pt<=500.0)+1.32046236765*(genBos_pt>500.0&&genBos_pt<=600.0)+1.26852513234*(genBos_pt>600.0))"

        z_ewkcorr = "(0.984525344338*(genBos_pt>100.0&&genBos_pt<=150.0)+0.969078612189*(genBos_pt>150.0&&genBos_pt<=200.0)+0.954626582726*(genBos_pt>200.0&&genBos_pt<=250.0)+0.941059330021*(genBos_pt>250.0&&genBos_pt<=300.0)+0.92828367065*(genBos_pt>300.0&&genBos_pt<=350.0)+0.916219976557*(genBos_pt>350.0&&genBos_pt<=400.0)+0.89931198024*(genBos_pt>400.0&&genBos_pt<=500.0)+0.878692669663*(genBos_pt>500.0&&genBos_pt<=600.0)+0.834717745177*(genBos_pt>600.0))"
        znlo012_over_zlo = "(1.68500099066*(genBos_pt>100.0&&genBos_pt<=150.0)+1.55256109189*(genBos_pt>150.0&&genBos_pt<=200.0)+1.52259467479*(genBos_pt>200.0&&genBos_pt<=250.0)+1.52062313572*(genBos_pt>250.0&&genBos_pt<=300.0)+1.4322825541*(genBos_pt>300.0&&genBos_pt<=350.0)+1.45741443405*(genBos_pt>350.0&&genBos_pt<=400.0)+1.36849777989*(genBos_pt>400.0&&genBos_pt<=500.0)+1.3580214432*(genBos_pt>500.0&&genBos_pt<=600.0)+1.16484769869*(genBos_pt>600.0))"
        #znlo012_over_zlo = "(1.0)"
        

        if postfit is True:
            #signal
            zm_postfit = "(1.01543666145*(met>200.0&&met<=250.0)+1.00878659009*(met>250.0&&met<=300.0)+0.992240701411*(met>300.0&&met<=350.0)+0.980790226127*(met>350.0&&met<=400.0)+0.992162508376*(met>400.0&&met<=500.0)+1.01709193399*(met>500.0&&met<=600.0)+0.971750393327*(met>600.0&&met<=1000.0))"
            wm_postfit = "(0.97616786892*(met>200.0&&met<=250.0)+0.992836206105*(met>250.0&&met<=300.0)+0.988815075206*(met>300.0&&met<=350.0)+0.990967690985*(met>350.0&&met<=400.0)+1.02663673098*(met>400.0&&met<=500.0)+1.03974881789*(met>500.0&&met<=600.0)+1.00280131711*(met>600.0&&met<=1000.0))"

            #control region
            #wm_postfit = " (0.946555651101*(met>200.0&&met<=250.0)+0.973055881969*(met>250.0&&met<=300.0)+0.986048794646*(met>300.0&&met<=350.0)+0.979567311538*(met>350.0&&met<=400.0)+1.00126342968*(met>400.0&&met<=500.0)+1.06766517518*(met>500.0&&met<=600.0)+1.00491247996*(met>600.0&&met<=1000.0) )"
            #zm_postfit = "(1.01468127004*(met>200.0&&met<=250.0)+1.00126753904*(met>250.0&&met<=300.0)+1.00090774129*(met>300.0&&met<=350.0)+0.965680804534*(met>350.0&&met<=400.0)+0.98662571148*(met>400.0&&met<=500.0)+1.0126394853*(met>500.0&&met<=600.0)+0.969938152304*(met>600.0&&met<=1000.0))"
            g_postfit = "(1.03612794076*(met>200.0&&met<=250.0)+1.02355494654*(met>250.0&&met<=300.0)+1.00738532306*(met>300.0&&met<=350.0)+0.991731959444*(met>350.0&&met<=400.0)+1.00189337175*(met>400.0&&met<=500.0)+0.995448261189*(met>500.0&&met<=600.0)+0.955212284288*(met>600.0&&met<=1000.0))"

            #"(0.974144987372*(met>200.0&&met<=250.0)+0.957144152837*(met>250.0&&met<=300.0)+0.924837461929*(met>300.0&&met<=350.0)+0.907693573019*(met>350.0&&met<=400.0)+0.897316971506*(met>400.0&&met<=500.0)+0.912633534821*(met>500.0&&met<=600.0)+0.877052889306*(met>600.0&&met<=1000.0))"
        else:
            wm_postfit = "(1.0)"
            zm_postfit = "(1.0)"
            g_postfit  = "(1.0)"
            

        # this is the scale using the total number of effective events
        scale = 1.0;
        scale = float(lumi)*physics_processes[Type]['xsec']/total
        
        #print '\n'
        print "type: ", Type,  "scale", scale, "lumi", lumi, physics_processes[Type]['xsec'], total

        if(shapelimits is True):
            # WRITING OUT A TREE
            file_out = ROOT.TFile("monojet_"+channel+".root", "update")
            if Type is 'data':
                if channel is 'signal':
                    selectedTree = input_tree.CopyTree( cut_standard + " && ((triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)) ");
                else:
                    selectedTree = input_tree.CopyTree( cut_standard );
            else:
                selectedTree = input_tree.CopyTree( cut_standard );

            scale_w = n.zeros(1,dtype=float)
            selectedTree.Branch('scale_w',scale_w,'scale_w/D')
            
            for i in range(selectedTree.GetEntries()):
                selectedTree.GetEntry(i)

                if Type is 'data':
                    scale_w[0] = 1.0
                else:
                    scale_w[0] = scale
                    
            selectedTree.Fill()
            selectedTree.Write(Type+"_"+channel)        
            file_out.Close()

            if Type.startswith('Zvv') or Type.startswith('Zll') or Type.startswith('Wlv') or Type.startswith('GJets') or Type.startswith('data'):
                if Type.startswith('Zvv') or Type.startswith('Zll') :
                    os.system('root -l -q -b "addMCWeight_zjets.C(\\"monojet_'+channel+'.root\\",\\"'+Type+'_'+channel+'\\")"')
                if Type.startswith('Wlv'):
                    os.system('root -l -q -b "addMCWeight_wjets.C(\\"monojet_'+channel+'.root\\",\\"'+Type+'_'+channel+'\\")"')
                if Type.startswith('GJets'):
                    os.system('root -l -q -b "addMCWeight_gjets.C(\\"monojet_'+channel+'.root\\",\\"'+Type+'_'+channel+'\\")"')
                if Type.startswith('data'):
                    os.system('root -l -q -b "addMCWeight_data.C(\\"monojet_'+channel+'.root\\",\\"'+Type+'_'+channel+'\\")"')
                    
            else: 
                os.system('root -l -q -b "addMCWeight.C(\\"monojet_'+channel+'.root\\",\\"'+Type+'_'+channel+'\\")"')


        if Type is not 'data' and Type is not 'signal_dm' and Type is not 'signal_dm_av_50_2' and Type is not 'signal_dm_av_1_2' and Type is not 'signal_dm_av_1_100' and Type is not 'signal_dm_av_10_100' and Type is not 'signal_dm_s_500_10' and Type is not 'signal_dm_s_500_1' and Type is not 'signal_dm_s_1_300' and Type is not 'signal_dm_s_50_300' and Type is not 'signal_h_vbf' and Type is not 'signal_h_ggf':
        #if Type is not 'data' and Type is not 'signal_dm' and Type is not 'signal_dm_s' and Type is not 'signal_dm_ps' and Type is not 'signal_dm_v' and Type is not 'signal_dm_av':
            Variables[Type].SetFillColor(physics_processes[Type]['color'])
            Variables[Type].SetLineColor(physics_processes[Type]['color'])

            if Type.startswith('GJets') :
                makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*0.98*"+str(g_postfit)+"*"+str(anlo1_over_alo)+"*"+str(a_ewkcorr)+"*" +str(w)+"*"+str(w_trig),"goff")

            elif (Type.startswith('Zvv') or Type.startswith('Zll')) :
                if channel is 'signal' :
                    makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*"+str(zm_postfit)+"*"+str(z_ewkcorr)+"*"+str(znlo012_over_zlo)+"*"+str(w)+"*"+str(w_trig),"goff")
                else:
                    makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*(0.98 *(lep1Eta<2.1)+0.91*(lep1Eta>=2.1))*"+str(zm_postfit)+"*"+str(z_ewkcorr)+"*"+str(znlo012_over_zlo)+"*"+str(w)+"*"+str(w_trig),"goff")


            elif Type.startswith('Wlv'):
                if channel is 'signal' :
                    makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*"+str(wm_postfit)+"*"+str(wnlo012_over_wlo)+"*"+str(w_ewkcorr)+"*" +str(w)+"*"+str(w_trig),"goff")
                else:                
                    makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*leptonSF*"+str(wm_postfit)+"*"+str(wnlo012_over_wlo)+"*"+str(w_ewkcorr)+"*" +str(w)+"*"+str(w_trig),"goff")
            
            else:
                makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ") *mcWeight*" +str(w)+"*"+str(w_trig),"goff")
                

            Variables[Type].Scale(scale,"width")
            stack.Add(Variables[Type],"hist")
            added.Add(Variables[Type])

        if Type.startswith('signal_h_ggf'):
            Variables[Type].SetLineColor(1)
            Variables[Type].SetLineWidth(3)
            Variables[Type].SetLineStyle(1)
            makeTrees(Type,"events",channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*"+str(w),"goff")
            Variables[Type].Scale(scale,"width")

        #if Type.startswith('signal_h_vbf'):
        if Type.startswith('signal_dm_av_1_2'):
            Variables[Type].SetLineColor(1)
            Variables[Type].SetLineWidth(3)
            Variables[Type].SetLineStyle(8)
            makeTrees(Type,"events",channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*"+str(w),"goff")
            Variables[Type].Scale(scale,"width")
            
        if Type.startswith('data'):
            Variables[Type].SetMarkerStyle(20)
            if channel is 'signal' or channel is 'Zmm' or channel is 'Wmn':
                makeTrees(Type,"events",channel).Draw(var + " >> " + histName, "(" + cut_standard + " && (triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1) )", "goff")
            else:
                makeTrees(Type,"events",channel).Draw(var + " >> " + histName, "(" + cut_standard +" )", "goff") 
            Variables[Type].Scale(1,"width")

        yield_dic[physics_processes[Type]['datacard']] += round(Variables[Type].Integral("width"),3)
        #print Type, round(Variables[Type].Integral(),3), "total in: ", physics_processes[Type]['datacard'],  yield_dic[physics_processes[Type]['datacard']]


    dump_datacard(channel,yield_dic)

    #added.Write()
            
    print 'INFO - Drawing the Legend', datetime.datetime.fromtimestamp( time.time())

    if channel is 'Zmm' or channel is 'Zee':
        legend = TLegend(.60,.65,.92,.92)
    elif channel is 'gjets':
        legend = TLegend(.60,.65,.82,.92)
    else:
        legend = TLegend(.60,.60,.92,.92)

    lastAdded = ''
    for process in  ordered_physics_processes:
        #print process
        Variables[process].SetTitle(process)
        if physics_processes[process]['label'] != lastAdded:
            lastAdded = physics_processes[process]['label']
            if process is not 'data' and process is not 'signal_dm' and process is not 'signal_dm_av_1_2' and process is not 'signal_h_ggf' and process is not 'signal_h_vbf':
                legend . AddEntry(Variables[process],physics_processes[process]['label'] , "f")
            if process is 'data':
                legend . AddEntry(Variables[process],physics_processes[process]['label'] , "p")
            #if process is 'signal_dm_av_1_2' or process is 'signal_dm':
            #if process is 'signal_h_ggf' or process is 'signal_h_vbf':
                #legend . AddEntry(Variables[process],physics_processes[process]['label'] , "l")


    c4 = TCanvas("c4","c4", 900, 1000)
    c4.SetBottomMargin(0.3)
    c4.SetRightMargin(0.06)

    stack.SetMinimum(0.01)
    #stack.SetMinimum(10)

    if setLog:
        c4.SetLogy()
        #stack.SetMaximum( stack.GetMaximum()  +  1e2*stack.GetMaximum() )
        stack.SetMaximum( stack.GetMaximum()  +  1e2*stack.GetMaximum() )
    else:
        #stack.SetMaximum( stack.GetMaximum()  +  1.5*stack.GetMaximum() )
        stack.SetMaximum( stack.GetMaximum()  +  0.5*stack.GetMaximum() )
    
    stack.Draw()
    stack.GetYaxis().SetTitle(ylabel)
    stack.GetYaxis().CenterTitle()
    stack.GetYaxis().SetTitleOffset(1.2)
    #stack.GetYaxis().SetTitleOffset(1.4)
    stack.GetXaxis().SetTitle(xlabel)
    stack.GetXaxis().SetLabelSize(0)
    stack.GetXaxis().SetTitle('')

    #Variables['data'].Draw("Esame")
    #if channel is not 'signal':
    #    Variables['data'].Draw("Esame")
    #else:

    #for b in range(Variables['data'].GetNbinsX()): Variables['data'].SetBinContent(b+1,0)
    Variables['data'].Draw("Esame")

    #Variables['data'].Draw("Esame")
    #if channel is 'signal' or channel is 'Zmm' or channel is 'Wmn':
    #Variables['signal_dm_av_1_2'].Draw("same")
        #Variables['signal_h_ggf'].Draw("same")
        #Variables['signal_h_vbf'].Draw("same")
    #else:
    #    Variables['signal_dm'].Draw("same")
    

    legend.SetShadowColor(0);
    legend.SetFillColor(0);
    legend.SetLineColor(0);

    legend.Draw("same")
    plot_cms(True,lumi_str)

    Pad = TPad("pad", "pad", 0.0, 0.0, 1.0, 1.0)
    Pad.SetTopMargin(0.7)
    Pad.SetFillColor(0)
    Pad.SetGridy(1)
    Pad.SetFillStyle(0)
    Pad.Draw()
    Pad.cd(0)
    Pad.SetRightMargin(0.06)
    
    data = Variables['data'].Clone()

    plot_ratio(False,data,added,bin,xlabel,0,2.0,5)

    #plot_ratio(False,data,added,bin,xlabel,0.5,1.5,5)
    #if channel is 'Zmm' or channel is 'Zee' or var is 'njets':
    #    plot_ratio(False,data,added,bin,xlabel,0,2.0,5)
        #plot_ratio(False,data,added,bin,xlabel,0.8,1.2,5)
    #else:
    #    plot_ratio(False,data,added,bin,xlabel,0.8,1.2,5)
                

    #if channel is not 'Wmn':
    #    plot_ratio(False,data,added,bin,xlabel,0,2,5)
    #else:
    #    plot_ratio(False,data,added,bin,xlabel,-1,3,10)

    f1 = TF1("f1","1",-5000,5000);
    f1.SetLineColor(4);
    f1.SetLineStyle(2);
    f1.SetLineWidth(2);
    f1.Draw("same")

    if postfit is True:
        if ht_bin:            
            c4.SaveAs(folder+'Histo_lov3_bin'+str(metcut)+'_Postfit' + name + '_'+channel+'.pdf')
            c4.SaveAs(folder+'Histo_lov3_bin'+str(metcut)+'_Postfit' + name + '_'+channel+'.png')
            c4.SaveAs(folder+'Histo_lov3_bin'+str(metcut)+'_Postfit' + name + '_'+channel+'.C')
        else:
            c4.SaveAs(folder+'Histo_lov3_Postfit' + name + '_'+channel+'.pdf')
            c4.SaveAs(folder+'Histo_lov3_Postfit' + name + '_'+channel+'.png')
            c4.SaveAs(folder+'Histo_lov3_Postfit' + name + '_'+channel+'.C')
            
    else:
        if ht_bin:
            c4.SaveAs(folder+'/Histo_lov3linear_bin'+str(metcut)+'_' + name + '_'+channel+'.pdf')
            c4.SaveAs(folder+'/Histo_lov3linear_bin'+str(metcut)+'_' + name + '_'+channel+'.png')
            c4.SaveAs(folder+'/Histo_lov3linear_bin'+str(metcut)+'_' + name + '_'+channel+'.C')
        else:
            #c4.SaveAs(folder+'/Histo_lov5_metfilter_' + name + '_'+channel+'.pdf')
            #c4.SaveAs(folder+'/Histo_lov5_metfilter_' + name + '_'+channel+'.png')
            #c4.SaveAs(folder+'/Histo_lov5_metfilter_' + name + '_'+channel+'.C')

            c4.SaveAs(folder+'/Histo_lov6_' + name + '_'+channel+'.pdf')
            c4.SaveAs(folder+'/Histo_lov6_' + name + '_'+channel+'.png')
            c4.SaveAs(folder+'/Histo_lov6_' + name + '_'+channel+'.C')

            #c4.SaveAs(folder+'/Histo_excitedquark_' + name + '_'+channel+'.pdf')
            #c4.SaveAs(folder+'/Histo_excitedquark_' + name + '_'+channel+'.png')
            #c4.SaveAs(folder+'/Histo_excitedquark' + name + '_'+channel+'.C')

    del Variables
    del var
    del f
    del h1
    c4.IsA().Destructor( c4 )
    stack.IsA().Destructor( stack )

arguments = {}
#                   = [var, bin, low, high, yaxis, xaxis, setLog]
arguments['met']    = ['met','met',16,200,1500,'Events/GeV','E_{T}^{miss} [GeV]',True]
arguments['jetpt']  = ['jetpt','jet1Pt',20,100,1500,'Events/GeV','Leading Jet P_{T} [GeV]',True]
#arguments['jetpt']  = ['jetpt','jet1Pt',9,100,1000,'Events/GeV','Leading Jet P_{T} [GeV]',True]
arguments['jet2pt']  = ['jet2pt','jet2Pt',36,100,2000,'Events/50 GeV','Leading Jet P_{T} [GeV]',True]
arguments['lep1Pt']  = ['lep1Pt','lep1Pt',20,0,1000,'Events/50 GeV','Leading Lepton P_{T} [GeV]',True]
arguments['lep2Pt']  = ['lep2Pt','lep2Pt',50,0,500,'Events/10 GeV','Trailing Lepton P_{T} [GeV]',True]
arguments['lep1PdgId'] = ['lep1PdgId','lep1PdgId',40,-20,20,'Events','Leading Lepton Pdg Id',True]
arguments['lep2PdgId'] = ['lep2PdgId','lep2PdgId',40,-20,20,'Events','Trailing Lepton Pdg Id',True]
arguments['jet1DPhiMet'] = ['jet1DPhiMet','jet1DPhiMet',100,0,10,'Events','DeltaPhi(Jet,Met)',True]
#arguments['minJetDPhi'] = ['minJetDPhi','minJetDPhi',50,0,5,'Events','minDeltaPhi(Jet,Met)',True]
arguments['dPhi_j1j2'] = ['dPhi_j1j2','dPhi_j1j2',50,0,5,'Events','Delta#Phi(Jet,Jet)',True]

arguments['njets']  = ['njets','n_jets',15,0,15,'Events','Number of Jets',True]
arguments['njetsclean']  = ['njetsclean','n_cleanedjets',15,0,15,'Events','Number of Jets',True]

arguments['njets_linear']  = ['njets_linear','n_jets',15,0,15,'Events','Number of Jets',False]
arguments['njetsclean_linear']  = ['njetsclean_linear','n_cleanedjets',15,0,15,'Events','Number of Jets',False]

#arguments['njetsclean']  = ['njetsclean','n_cleanedjjets',5,1,6,'Events','Number of Jets',True]

arguments['n_looselep']  = ['n_looselep','n_looselep',6,0,6,'Events','Number of Loose Leptons',True]
arguments['n_loosepho']  = ['n_loosepho','n_loosepho',6,0,6,'Events','Number of Loose Photons',True]
arguments['n_tightpho']  = ['n_tightpho','n_tightpho',6,0,6,'Events','Number of Tight Photons',True]
arguments['n_tau']       = ['n_tau','n_tau',6,0,6,'Events','Number of Loose Taus',True]
arguments['n_bjetsMedium']  = ['n_bjetsMedium','n_bjetsMedium',6,0,6,'Events','Number of Medium b-Jets',True]
#arguments['jet1Eta'] = ['jet1Eta','jet1Eta',40,-4.0,4.0,'Events','Jet #eta',False]
arguments['npv']    = ['npv','npv',30,0,30,'Events','Number of Primary Vertex',True]
arguments['phoPt']  = ['phoPt','photonPt',18,100,1000,'Events/50 GeV','p_{T}^{#gamma} [GeV]',True]
arguments['phoPhi'] = ['phoPhi','photonP4.Phi()',40,-4.0,4.0,'Events/50 GeV','#phi',False]
arguments['metRaw'] = ['metRaw','metRaw',16,200,1000,'Events/50 GeV','Raw E_{T}^{miss} [GeV]',True]
arguments['genmet'] = ['genmet','genmet',16,200,1000,'Events/50 GeV','Generated E_{T}^{miss} [GeV]',True]
arguments['trueMet']    = ['trueMet','trueMet',10,0,500,'Events/GeV','E_{T}^{miss} [GeV]',True]
arguments['mt']     = ['mt','mt',50,0,1000,'Events/20 GeV','M_{T} [GeV]',True]
arguments['u_magW'] = ['u_magW','u_magW',50,0,1000,'Evtents/20 GeV','U [GeV]',True]
arguments['dphilep_truemet'] = ['dphilep_truemet','deltaPhi(lep1Phi,trueMetPhi)',40,0,4.0,'Events','DPhi(lep,met)',True]
arguments['minJetMetDPhi'] = ['minJetMetDPhi','minJetMetDPhi',40,0,4.0,'Events','min DPhi(jet,met)',False]
arguments['mt_new']  = ['mt_new','transverseMass(lep1Pt,lep1Phi,trueMet,trueMetPhi)',50,0,1000,'Events','M_{T} New [GeV]',True]
arguments['dilep_m']  = ['dilep_m','dilep_m',50,60,160,'Events/2 [GeV]','Dilepton Mass [GeV]',True]
arguments['dilep_pt']  = ['dilep_pt','dilep_pt',12,0,600,'Events / 50 GeV','Dilepton Pt [GeV]',True]
arguments['dRjlep'] = ['dRjlep','deltaR(lep1Phi,lep1Eta,jet1Phi,jet1Eta)',60,0,6,'Events','DeltaR(lep1,jet)',True ]
arguments['dRjlep2'] = ['dRjlep2','deltaR(lep2Phi,lep2Eta,jet1Phi,jet1Eta)',60,0,6,'Events','DeltaR(lep2,jet)',True ]


arguments['dRplep'] = ['dRplep','deltaR(lep1Phi,lep1Eta,photonPhi,photonEta)',60,0,6,'Events','DeltaR(lep1,photon)',True ]

arguments['jet1Phi'] = ['jet1Phi','jet1Phi',40,-4.0,4.0,'Events','#phi',True]


arguments['phoEta']  = ['phoEta','photonEta',40,-2.0,2.0,'Events','#eta (#gamma)',False]
arguments['lep1Eta'] = ['lep1Eta','lep1Eta',40,-3.0,3.0,'Events','#eta (l)',False]
arguments['dilepEta'] = ['dilep_eta','dilep_eta',40,-3.0,3.0,'Events','#eta (ll)',False]
arguments['jet1Eta'] = ['jet1Eta','jet1Eta',40,-3.0,3.0,'Events','#eta (leading jet)',False]

arguments['ht']          = ['ht','ht',20,0,2000,'Events/GeV','H_{T} [GeV]',True]
arguments['ht_cleaned']  = ['ht_cleaned','ht_cleaned',20,0,2000,'Events/GeV','H_{T} [GeV]',True]

arguments['gj_mass'] = ['gj_mass',
                        'vectormass(photonPt, photonPhi, photonEta, jet1Pt, jet1Phi, jet1Eta)',
                        40,0,4000,'Events/GeV','M_{#gamma,j} [GeV]',True]

#channel_list  = ['signal','Wmn','Zmm']
#channel_list  = ['Wen','Zee']
channel_list  = ['gjets']

#channel_list = ['Wmn','Zmm']
#channel_list = ['signal']

#channel_list = ['Zmm']
#channel_list = ['Wmn']


processes     = []

#variable_list = ['gj_mass','trueMet']
#variable_list = ['met']
#variable_list = ['njets','njetsclean']
#variable_list = ['jetpt']
variable_list = ['jetpt','njetsclean']
#variable_list = ['jetpt','njets','njetsclean','njets_linear','njetsclean_linear']

#variable_list = ['ht','ht_cleaned']
#variable_list = ['met','jetpt','njets','jet1Eta','minJetMetDPhi']
#variable_list = ['minJetMetDPhi']

#variable_list = ['phoEta','lep1Eta','dilepEta']
#variable_list = ['met','jetpt','lep1Pt','dilep_pt','njets','phoPt','dPhi_j1j2','jet2pt','phoEta','dilep_eta','jet_eta']
#variable_list = ['jet1Phi']
#variable_list = ['met','jetpt','njets','npv']
#variable_list = ['met','jetpt','njets','n_looselep','n_loosepho','n_tightpho','npv','mt', 'lep1Pt']
#variable_list = ['met','jetpt','njets','n_looselep','n_loosepho','n_tightpho','npv','dilep_m', 'dilep_pt', 'lep1Pt']
#variable_list = ['met','jetpt','njets','n_looselep','n_loosepho','n_tightpho','npv','phoPt']

start_time = time.time()

for channel in channel_list:
    for var in variable_list:
        arguments[var].insert(0,channel)
        print  arguments[var]
        process = Process(target = plot_stack, args = arguments[var])
        process.start()
        processes.append(process)
        arguments[var].remove(channel)
for process in processes: 
    process.join()

print("--- %s seconds ---" % (time.time()-start_time))
print datetime.datetime.fromtimestamp(time.time()-start_time)
