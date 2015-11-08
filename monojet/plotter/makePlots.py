#! /usr/bin/env python
import sys, os, string, re, time, datetime
from multiprocessing import Process
from array import array

from LoadData import *
#from LoadGJets import *
#from LoadElectron import *

from ROOT import *
from math import *
from tdrStyle import *
from selection import build_selection
from datacard import dump_datacard
from pretty import plot_ratio, plot_cms

import numpy as n

setTDRStyle()

print "Starting Plotting Be Patient!"

lumi = 1264.
shapelimits = False

def plot_stack(channel, name,var, bin, low, high, ylabel, xlabel, setLog = False):

    folder = '/afs/cern.ch/user/z/zdemirag/www/Monojet/topup/'
    if not os.path.exists(folder):
        os.mkdir(folder)

    yield_dic = {}

    stack = THStack('a', 'a')
    if var is 'met':
        binLowE = [200,250,300,350,400,500,600,1000]
        added = TH1D('added','added',7,array('d',binLowE))
    else:
        added = TH1D('added', 'added',bin,low,high)
    added.Sumw2()
    f  = {}
    h1 = {}

    Variables = {}    
    #cut_standard= build_selection(channel,0) ### Fix this back to 200 ###
    #cut_standard= build_selection(channel,200) ### Fix this back to 200 ###
    cut_standard= build_selection(channel,400) ### Fix this back to 200 ###

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
            binLowE = [200,250,300,350,400,500,600,1000]
            Variables[Type] = TH1F(histName,histName,7,array('d',binLowE))
        else:
            Variables[Type] = TH1F(histName, histName, bin, low, high)

        Variables[Type].Sumw2()
        #print "\n"

        # this right now breaks the tchain logic! 
        # if we have more than 1 file, this will break!!!!  
        #print physics_processes[Type]['files'][0]
        f[Type] = ROOT.TFile(physics_processes[Type]['files'][0],"read")
        h1[Type] = f[Type].Get("htotal")
        total = h1[Type].GetBinContent(1)
        f[Type].Close()
        
        input_tree   = makeTrees(Type,"events",channel)
        n_entries = input_tree.GetEntries()

        #Incase you want to apply event by event re-weighting
        #w = 1.0;
        w = '(3.57041 + -1.49846*npv + 0.515829*npv*npv + -0.0839209*npv*npv*npv + 0.00719964*npv*npv*npv*npv + -0.000354548*npv*npv*npv*npv*npv + 1.01544e-05*npv*npv*npv*npv*npv*npv + -1.58019e-07*npv*npv*npv*npv*npv*npv*npv + 1.03663e-09*npv*npv*npv*npv*npv*npv*npv*npv)'

        anlo1_over_alo = "(1.24087232993*(genBos_pt>100.0&&genBos_pt<=150.0)+1.55807026252*(genBos_pt>150.0&&genBos_pt<=200.0)+1.51043242876*(genBos_pt>200.0&&genBos_pt<=250.0)+1.47333461572*(genBos_pt>250.0&&genBos_pt<=300.0)+1.43497331471*(genBos_pt>300.0&&genBos_pt<=350.0)+1.37846354687*(genBos_pt>350.0&&genBos_pt<=400.0)+1.2920177717*(genBos_pt>400.0&&genBos_pt<=500.0)+1.31414429236*(genBos_pt>500.0&&genBos_pt<=600.0)+1.20453974747*(genBos_pt>600.0&&genBos_pt<=1000.0))"
        
        a_ewkcorr = "(0.998568444581*(genBos_pt>100.0&&genBos_pt<=150.0)+0.992098286517*(genBos_pt>150.0&&genBos_pt<=200.0)+0.986010290609*(genBos_pt>200.0&&genBos_pt<=250.0)+0.980265498435*(genBos_pt>250.0&&genBos_pt<=300.0)+0.974830448283*(genBos_pt>300.0&&genBos_pt<=350.0)+0.969676202351*(genBos_pt>350.0&&genBos_pt<=400.0)+0.962417128177*(genBos_pt>400.0&&genBos_pt<=500.0)+0.953511139209*(genBos_pt>500.0&&genBos_pt<=600.0)+0.934331895615*(genBos_pt>600.0&&genBos_pt<=1000.0))"

        w_ewkcorr = "(0.980859240872*(genBos_pt>100.0&&genBos_pt<=150.0)+0.962118764182*(genBos_pt>150.0&&genBos_pt<=200.0)+0.944428528597*(genBos_pt>200.0&&genBos_pt<=250.0)+0.927685912907*(genBos_pt>250.0&&genBos_pt<=300.0)+0.911802238928*(genBos_pt>300.0&&genBos_pt<=350.0)+0.896700388113*(genBos_pt>350.0&&genBos_pt<=400.0)+0.875368225896*(genBos_pt>400.0&&genBos_pt<=500.0)+0.849096933047*(genBos_pt>500.0&&genBos_pt<=600.0)+0.792158791839*(genBos_pt>600.0&&genBos_pt<=1000.0))"

        wnlo012_over_wlo = "(1.88495975436*(genBos_pt>100.0&&genBos_pt<=150.0)+1.70131638907*(genBos_pt>150.0&&genBos_pt<=200.0)+1.68926939542*(genBos_pt>200.0&&genBos_pt<=250.0)+1.54863611231*(genBos_pt>250.0&&genBos_pt<=300.0)+1.51196636307*(genBos_pt>300.0&&genBos_pt<=350.0)+1.4*(genBos_pt>350.0))"
        #wnlo012_over_wlo = "(1.88495975436*(genBos_pt>100.0&&genBos_pt<=150.0)+1.70131638907*(genBos_pt>150.0&&genBos_pt<=200.0)+1.68926939542*(genBos_pt>200.0&&genBos_pt<=250.0)+1.54863611231*(genBos_pt>250.0&&genBos_pt<=300.0)+1.51196636307*(genBos_pt>300.0&&genBos_pt<=350.0)+1.32308306674*(genBos_pt>350.0&&genBos_pt<=400.0)+1.21366409789*(genBos_pt>400.0&&genBos_pt<=500.0)+0.895193819547*(genBos_pt>500.0&&genBos_pt<=600.0)+1.49473180298*(genBos_pt>600.0&&genBos_pt<=1000.0))"

        z_ewkcorr ="(0.984525344338*(genBos_pt>100.0&&genBos_pt<=150.0)+0.969078612189*(genBos_pt>150.0&&genBos_pt<=200.0)+0.954626582726*(genBos_pt>200.0&&genBos_pt<=250.0)+0.941059330021*(genBos_pt>250.0&&genBos_pt<=300.0)+0.92828367065*(genBos_pt>300.0&&genBos_pt<=350.0)+0.916219976557*(genBos_pt>350.0&&genBos_pt<=400.0)+0.89931198024*(genBos_pt>400.0&&genBos_pt<=500.0)+0.878692669663*(genBos_pt>500.0&&genBos_pt<=600.0)+0.834717745177*(genBos_pt>600.0&&genBos_pt<=1000.0))"


        # this is the scale using the total number of effective events
        scale = 1.0;
        scale = float(lumi)*physics_processes[Type]['xsec']/total
        
        #print '\n'
        print "type: ", Type,  "scale", scale, "lumi", lumi, physics_processes[Type]['xsec'], total

        if(shapelimits is True):
            # WRITING OUT A TREE
            file_out = ROOT.TFile("monojet_"+channel+".root", "update")
            if Type is 'data':
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

        if Type is not 'data' and Type is not 'signal_dm':
            Variables[Type].SetFillColor(physics_processes[Type]['color'])
            Variables[Type].SetLineColor(physics_processes[Type]['color'])
            if Type.startswith('GJets') :
                #makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*kfactor*" +str(w),"goff")            
                #makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*1.5*" +str(w),"goff")            
                makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*"+str(anlo1_over_alo)+"*"+str(a_ewkcorr)+"*" +str(w),"goff")
            elif (Type.startswith('Zvv') or Type.startswith('Zll')) :
                makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*"+str(z_ewkcorr)+"*"+str(w),"goff")
            elif Type.startswith('Wlv'):
                makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*"+str(wnlo012_over_wlo)+"*"+str(w_ewkcorr)+"*" +str(w),"goff")
                #makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*0.0*" +str(w),"goff")
                #makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*" +str(w),"goff")
            else:
                makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*" +str(w),"goff")
            Variables[Type].Scale(scale,"width")
            stack.Add(Variables[Type],"hist")
            added.Add(Variables[Type])

        if Type.startswith('signal_dm'):
            Variables[Type].SetLineColor(1)
            Variables[Type].SetLineWidth(3)
            Variables[Type].SetLineStyle(8)
            makeTrees(Type,"events",channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*"+str(w),"goff")
            Variables[Type].Scale(scale,"width")
            
        if Type.startswith('data'):
            Variables[Type].SetMarkerStyle(20)
            #if channel is 'signal':
            #    makeTrees(Type,"events",channel).Draw(var + " >> " + histName, "(" + cut_standard + "&& (triggerFired[1]==1 || triggerFired[0]==1 || triggerFired[2]==1 ))", "goff")
            #else:
            makeTrees(Type,"events",channel).Draw(var + " >> " + histName, "(" + cut_standard + ")", "goff")
            Variables[Type].Scale(1,"width")

        yield_dic[physics_processes[Type]['datacard']] += round(Variables[Type].Integral("width"),3)
        print Type, round(Variables[Type].Integral(),3), "total in: ", physics_processes[Type]['datacard'],  yield_dic[physics_processes[Type]['datacard']]

    dump_datacard(channel,yield_dic)

    #added.Write()
            
    print 'INFO - Drawing the Legend', datetime.datetime.fromtimestamp( time.time())

    legend = TLegend(.60,.60,.92,.92)
    lastAdded = ''
    for process in  ordered_physics_processes:
        #print process
        Variables[process].SetTitle(process)
        if physics_processes[process]['label'] != lastAdded:
            lastAdded = physics_processes[process]['label']
            if process is not 'data' and process is not 'signal_dm': 
                legend . AddEntry(Variables[process],physics_processes[process]['label'] , "f")
            if process is 'data':
                legend . AddEntry(Variables[process],physics_processes[process]['label'] , "p")
            if process is 'signal_dm':
                legend . AddEntry(Variables[process],physics_processes[process]['label'] , "l")


    c4 = TCanvas("c4","c4", 900, 1000)
    c4.SetBottomMargin(0.3)
    c4.SetRightMargin(0.06)

    stack.SetMinimum(0.01)

    if setLog:
        c4.SetLogy()
        stack.SetMaximum( stack.GetMaximum()  +  100*stack.GetMaximum() )
    else:
        stack.SetMaximum( stack.GetMaximum()  +  stack.GetMaximum() )
    
    stack.Draw()
    stack.GetYaxis().SetTitle(ylabel)
    stack.GetYaxis().CenterTitle()
    stack.GetYaxis().SetTitleOffset(1.2)
    stack.GetXaxis().SetTitle(xlabel)
    stack.GetXaxis().SetLabelSize(0)
    stack.GetXaxis().SetTitle('')

    if channel is not 'signal':
        Variables['data'].Draw("Esame")
    else:
        for b in range(Variables['data'].GetNbinsX()): Variables['data'].SetBinContent(b+1,0)
        Variables['data'].Draw("Esame")

    Variables['signal_dm'].Draw("same")
    
    legend.SetShadowColor(0);
    legend.SetFillColor(0);
    legend.SetLineColor(0);

    legend.Draw("same")
    plot_cms(True,lumi)

    Pad = TPad("pad", "pad", 0.0, 0.0, 1.0, 1.0)
    Pad.SetTopMargin(0.7)
    Pad.SetFillColor(0)
    Pad.SetGridy(1)
    Pad.SetFillStyle(0)
    Pad.Draw()
    Pad.cd(0)
    Pad.SetRightMargin(0.06)
    
    data = Variables['data'].Clone()
    if channel is not 'Wmn':
        plot_ratio(False,data,added,bin,xlabel,0,2,5)
    else:
        plot_ratio(False,data,added,bin,xlabel,-1,3,10)

    f1 = TF1("f1","1",-5000,5000);
    f1.SetLineColor(4);
    f1.SetLineStyle(2);
    f1.SetLineWidth(2);
    f1.Draw("same")

    c4.SaveAs(folder+'/'+channel+'/Histo_' + name + '_'+channel+'.pdf')
    c4.SaveAs(folder+'/'+channel+'/Histo_' + name + '_'+channel+'.png')
    c4.SaveAs(folder+'/'+channel+'/Histo_' + name + '_'+channel+'.C')

    del Variables
    del var
    del f
    del h1
    c4.IsA().Destructor( c4 )
    stack.IsA().Destructor( stack )

arguments = {}
#                   = [var, bin, low, high, yaxis, xaxis, setLog]
arguments['met']    = ['met','met',16,200,1000,'Events/GeV','E_{T}^{miss} [GeV]',True]
arguments['jetpt']  = ['jetpt','jet1Pt',100,0,1000,'Events/20 GeV','Leading Jet P_{T} [GeV]',True]
arguments['lep1Pt']  = ['lep1Pt','lep1Pt',50,0,500,'Events/10 GeV','Leading Lepton P_{T} [GeV]',True]
arguments['lep2Pt']  = ['lep2Pt','lep2Pt',50,0,500,'Events/10 GeV','Trailing Lepton P_{T} [GeV]',True]
arguments['lep1PdgId'] = ['lep1PdgId','lep1PdgId',40,-20,20,'Events','Leading Lepton Pdg Id',True]
arguments['lep2PdgId'] = ['lep2PdgId','lep2PdgId',40,-20,20,'Events','Trailing Lepton Pdg Id',True]
arguments['jet1DPhiMet'] = ['jet1DPhiMet','jet1DPhiMet',10,0,5,'Events','DeltaPhi(Jet,Met)',True]
#arguments['minJetDPhi'] = ['minJetDPhi','minJetDPhi',50,0,5,'Events','minDeltaPhi(Jet,Met)',True]
arguments['dPhi_j1j2'] = ['dPhi_j1j2','dPhi_j1j2',10,0,5,'Events','DeltaPhi(Jet,Jet)',True]
arguments['njets']  = ['njets','n_jets',10,0,10,'Events','Number of Jets',True]
arguments['n_looselep']  = ['n_looselep','n_looselep',6,0,6,'Events','Number of Loose Leptons',True]
arguments['n_loosepho']  = ['n_loosepho','n_loosepho',6,0,6,'Events','Number of Loose Photons',True]
arguments['n_tightpho']  = ['n_tightpho','n_tightpho',6,0,6,'Events','Number of Tight Photons',True]
arguments['n_tau']       = ['n_tau','n_tau',6,0,6,'Events','Number of Loose Taus',True]
arguments['n_bjetsMedium']  = ['n_bjetsMedium','n_bjetsMedium',6,0,6,'Events','Number of Medium b-Jets',True]
arguments['jet1Eta'] = ['jet1Eta','jet1Eta',40,-4.0,4.0,'Events','Jet #eta',False]
arguments['npv']    = ['npv','npv',30,0,30,'Events','Number of Primary Vertex',True]
arguments['njetsclean']  = ['njetsclean','n_cleanedjets',5,1,6,'Events','Number of Jets',True]
arguments['phoPt']  = ['phoPt','photonPt',90,100,1000,'Events/10 GeV','p_{T}^{#gamma} [GeV]',True]
arguments['phoEta'] = ['phoEta','photonEta',40,-3.0,3.0,'Events/50 GeV','#eta',False]
arguments['phoPhi'] = ['phoPhi','photonP4.Phi()',40,-4.0,4.0,'Events/50 GeV','#phi',False]
arguments['metRaw'] = ['metRaw','metRaw',16,200,1000,'Events/50 GeV','Raw E_{T}^{miss} [GeV]',True]
arguments['genmet'] = ['genmet','genmet',16,200,1000,'Events/50 GeV','Generated E_{T}^{miss} [GeV]',True]
arguments['trueMet']    = ['trueMet','trueMet',50,0,1000,'Events/50 GeV','E_{T}^{miss} [GeV]',True]
arguments['mt']     = ['mt','mt',50,0,1000,'Events/20 GeV','M_{T} [GeV]',True]
arguments['u_magW'] = ['u_magW','u_magW',50,0,1000,'Events/20 GeV','U [GeV]',True]
arguments['dphilep_truemet'] = ['dphilep_truemet','deltaPhi(lep1Phi,trueMetPhi)',40,0,4.0,'Events','DPhi(lep,met)',True]
arguments['minJetMetDPhi'] = ['minJetMetDPhi','minJetMetDPhi',40,0,4.0,'Events','min DPhi(jet,met)',True]
arguments['mt_new']  = ['mt_new','transverseMass(lep1Pt,lep1Phi,trueMet,trueMetPhi)',50,0,1000,'Events','M_{T} New [GeV]',True]
arguments['dilep_m']  = ['dilep_m','dilep_m',50,60,160,'Events/2 [GeV]','Dilepton Mass [GeV]',True]
arguments['dilep_pt']  = ['dilep_pt','dilep_pt',50,0,1000,'Events','Dilepton Pt [GeV]',True]
arguments['dRjlep'] = ['dRjlep','deltaR(lep1Phi,lep1Eta,jet1Phi,jet1Eta)',60,0,6,'Events','DeltaR(lep1,jet)',True ]
arguments['dRjlep2'] = ['dRjlep2','deltaR(lep2Phi,lep2Eta,jet1Phi,jet1Eta)',60,0,6,'Events','DeltaR(lep2,jet)',True ]


#channel_list  = ['signal','Wmn','Zmm']
#channel_list  = ['Wen','Zee']
#channel_list  = ['gjets']

channel_list = ['Zmm']

processes     = []

variable_list = ['met']
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
