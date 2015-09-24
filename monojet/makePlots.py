#! /usr/bin/env python

import sys, os, string, re, time, datetime
from multiprocessing import Process
from array import array
#from LoadData import *
from LoadMonoPhoton import *
from ROOT import *
from math import *
from tdrStyle import *
from selection import build_selection
from datacard import dump_datacard
from pretty import plot_ratio, plot_cms

setTDRStyle()
gROOT.LoadMacro("functions.C+");

print "Starting Plotting Be Patient!"

lumi = 15.480

cut_goodruns = "(runNum == 1 || (runNum == 254231 && (lumiNum >=1 && lumiNum <= 24)) || (runNum == 254232 && (lumiNum >= 1 && lumiNum <= 81)) || (runNum == 254790 && ((lumiNum == 90) || (lumiNum >= 93 && lumiNum <= 630) || (lumiNum >= 633 && lumiNum <= 697) || (lumiNum >= 701 && lumiNum <= 715) || (lumiNum >= 719 && lumiNum <= 784))) || (runNum == 254852 && (lumiNum >= 47 && lumiNum <= 94)) || (runNum == 254879 && ((lumiNum == 52) || (lumiNum >= 54 && lumiNum <= 140))) || (runNum == 254906 && (lumiNum >= 1 && lumiNum <= 75)) || (runNum == 254907 && (lumiNum >= 1 && lumiNum <=52)))"

def plot_stack(channel, name,var, bin, low, high, ylabel, xlabel, setLog = False):

    folder = 'output'
    if not os.path.exists(folder):
        os.mkdir(folder)

    yield_Zll = {}
    yield_dic = {}
    yield_Wln = {}
    yield_signal = {}
    stack = THStack('a', 'a')
    added = TH1D('a', 'a',bin,low,high)
    added.Sumw2()
    f  = {}
    h1 = {}

    Variables = {}    
    cut_standard= build_selection(channel,100) ### Fix this back to 200 ###
    print "INFO Channel is: ", channel, " variable is: ", var, " Selection is: ", cut_standard,"\n"
    print 'INFO time is:', datetime.datetime.fromtimestamp( time.time())

    reordered_physics_processes = []
    if channel == 'Zll': reordered_physics_processes = reversed(ordered_physics_processes)
    else: reordered_physics_processes = ordered_physics_processes
 
    for Type in reordered_physics_processes:
        # Create the Histograms
        histName = Type+'_'+name+'_'+channel
        Variables[Type] = TH1F(histName, histName, bin, low, high)
        Variables[Type].Sumw2()

        print "\n"
        # this right now breaks the tchain logic! 
        # if we have more than 1 file, this will break!!!!  
        print physics_processes[Type]['files'][0]
        f[Type] = ROOT.TFile(physics_processes[Type]['files'][0],"read")
        h1[Type] = f[Type].Get("htotal")
        tempTree = f[Type].Get("all")
        tempTree.GetEntry(0)
        total = h1[Type].GetBinContent(1)/abs(tempTree.mcWeight)
        f[Type].Close()
        
        input_tree   = makeTrees(Type,"events",channel)
        n_entries = input_tree.GetEntries()

        #Incase you want to apply event by event re-weighting
        w = 1.0;
        # this is the scale using the total number of effective events
        scale = 1.0;
        scale = float(lumi)*physics_processes[Type]['xsec']/total
        
        print "type: ", Type, "weight", w, "scale", scale, "lumi", lumi, physics_processes[Type]['xsec'], total

        if Type.startswith('QCD') or Type.startswith('Zll') or \
        Type.startswith('others') or Type.startswith('Wlv') or \
        Type.startswith('Zvv') or Type.startswith('GJets'):
            Variables[Type].SetFillColor(physics_processes[Type]['color'])
            Variables[Type].SetLineColor(physics_processes[Type]['color'])
            makeTrees(Type,'events',channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*" +str(w),"goff")
            print "integral: " + str(Variables[Type].Integral())
            Variables[Type].Scale(scale)
            #print "Type: ", Type, "Total Events:", scale* Variables[Type].GetEntries() , "scale", scale, "raw events", Variables[Type].GetEntries()
            stack.Add(Variables[Type],"hist")
            added.Add(Variables[Type])

        if Type.startswith('signal_higgs'):
            Variables[Type].SetLineColor(1)
            Variables[Type].SetLineWidth(3)
            Variables[Type].SetLineStyle(8)
            makeTrees(Type,"events",channel).Draw(var + " >> " + histName,"(" + cut_standard + ")*mcWeight*"+str(w),"goff")
            Variables[Type].Scale(scale)
                        
        if Type.startswith("data"):
            Variables[Type].SetMarkerStyle(20)
            makeTrees(Type,"events",channel).Draw(var + " >> " + histName,  "(" + cut_standard + "&&" + cut_goodruns + ")*mcWeight*"+str(w), "goff")
        
        yield_dic[Type] = round(Variables[Type].Integral(),3)

    dump_datacard(channel,yield_dic)

    #added.Write()
            
    print 'INFO - Drawing the Legend', datetime.datetime.fromtimestamp( time.time())

    legend = TLegend(.60,.60,.92,.92)
    lastAdded = ''
    for process in  ordered_physics_processes:
        Variables[process].SetTitle(process)
        #Variables[process].Write()
        if physics_processes[process]['label'] != lastAdded:
            lastAdded = physics_processes[process]['label']
            if process is not 'data' and process is not 'Zvv_ht200' and process is not 'Zvv_ht400' and process is not 'Zvv_ht600': 
                legend . AddEntry(Variables[process],physics_processes[process]['label'] , "f")
            if process is 'data':
                legend . AddEntry(Variables[process],physics_processes[process]['label'] , "p")

    c4 = TCanvas("c4","c4", 900, 1000)
    c4.SetBottomMargin(0.3)
    c4.SetRightMargin(0.06)

    stack.SetMinimum(0.1)

    if setLog:
        c4.SetLogy()
        stack.SetMaximum( stack.GetMaximum()  +  1000*stack.GetMaximum() )
    
    stack.Draw()
    stack.GetYaxis().SetTitle(ylabel)
    stack.GetYaxis().CenterTitle()
    stack.GetXaxis().SetTitle(xlabel)
    stack.GetXaxis().SetLabelSize(0)
    stack.GetXaxis().SetTitle('')

    Variables['data'].Draw("Esame")
    Variables['signal_higgs'].Draw("same")
    
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
    plot_ratio(False,data,added,bin,xlabel)

    f1 = TF1("f1","1",-5000,5000);
    f1.SetLineColor(4);
    f1.SetLineStyle(2);
    f1.SetLineWidth(2);
    f1.Draw("same")

    c4.SaveAs(folder+'/Histo_' + name + '_'+channel+'.pdf')

    del Variables
    del var
    del f
    del h1
    c4.IsA().Destructor( c4 )
    stack.IsA().Destructor( stack )

arguments = {}
#                = [var, bin, low, high, yaxis, xaxis, setLog]
arguments['met']    = ['met','metP4.Pt()',16,200,1000,'Events/50 GeV','E_{T}^{miss} [GeV]',True]   ### Fix this back to 16,200,1000 ###
arguments['metRaw'] = ['metRaw','metRaw',16,200,1000,'Events/50 GeV','Raw E_{T}^{miss} [GeV]',True]
arguments['genmet'] = ['genmet','genmet',16,200,1000,'Events/50 GeV','Generated E_{T}^{miss} [GeV]',True]
arguments['jetpt']  = ['jetpt','jet1.pt()',17,150,1000,'Events/50 GeV','Leading Jet P_{T} [GeV]',True]
arguments['njets']  = ['njets','njets',3,1,4,'Events','Number of Jets',True]

#channel_list = ['signal']
#channel_list  = ['signal','Wln','Zll']
channel_list  = ['monophoton']
#channel_list  = ['Zll']
#variable_list = ['met','jetpt','njets','metRaw','genmet']
processes     = []

variable_list = ['met']

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
