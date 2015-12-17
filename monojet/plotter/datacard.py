import sys, os, string, re

if not os.path.exists('datacards'):
    os.mkdir('datacards')

def dump_datacard(channel,yields_dic):
    nprocess = 0
    yields_slim = {}
    for process in yields_dic.keys():
        nprocess += 1
        if process not in 'data' and process not in 'signal':
            yields_slim[process]=yields_dic[process]
            
    datacard = open('datacards/datacard_'+channel+'.txt', 'w')
    datacard.write('')
    datacard.write( 'imax 1 number of bins \n') 
    datacard.write( 'jmax '+str(nprocess-2)+' number of processes minus 1 \n') # -1 for data
    datacard.write( 'kmax * number of nuisance parameters \n')
    datacard.write( '----------------------------------------------------------------------------------------------------------------------------------------------\n')
    datacard.write( 'shapes * '+channel+' FAKE \n')
    datacard.write( '----------------------------------------------------------------------------------------------------------------------------------------------\n')
    datacard.write('bin                 ' +channel+'\n')
    datacard.write('observation         ' +str(yields_dic['data']) + '\n')
    datacard.write( '----------------------------------------------------------------------------------------------------------------------------------------------\n')
    datacard.write('{0:40s}'.format('bin'))
    for process in yields_dic.keys():
        if process not in 'data':
            datacard.write('{0:20s}'.format(channel))
    datacard.write('\n')
    datacard.write('{0:40s}'.format('process'))
    datacard.write('{0:20s}'.format('signal'))
    for process in yields_slim.keys():
        datacard.write('{0:20s}'.format(process))
    datacard.write('\n')
    datacard.write('{0:21s}'.format('process'))
    datacard.write('{0:20d}'.format(0))
    for num, process in enumerate(yields_slim.keys()):
        datacard.write('{0:20d}'.format(num+1))
    datacard.write('\n')
    datacard.write('{0:21s}'.format('rate'))
    datacard.write('{0:20.3f}'.format(yields_dic['signal']))
    for process in yields_slim.keys():
        datacard.write('{0:20.3f}'.format(yields_dic[process]))
    datacard.write('\n')
    datacard.write( '----------------------------------------------------------------------------------------------------------------------------------------------\n')
    datacard.write('{0:20s}'.format('syst_'+channel+'_bkg'))
    datacard.write('{0:20s}'.format('lnN'))
    for process in yields_dic.keys():        
        if process not in 'data':
            datacard.write('{0:20s}'.format('-'))
    datacard.write('\n')
    datacard.write('{0:20s}'.format('syst_'+channel+'_sig'))
    datacard.write('{0:20s}'.format('lnN'))
    for process in yields_dic.keys():
        if process not in 'data':
            datacard.write('{0:20s}'.format('-'))
    datacard.write('\n')
    datacard.write('{0:20s}'.format('syst_Zjets_norm'))
    datacard.write('{0:20s}'.format('lnU'))
    for process in yields_dic.keys():
        if process not in 'data':
            datacard.write('{0:20s}'.format('-'))
    datacard.write('\n') 
    datacard.write('{0:20s}'.format('syst_WJets_norm'))
    datacard.write('{0:20s}'.format('lnU'))
    for process in yields_dic.keys():
        if process not in 'data':
            datacard.write('{0:20s}'.format('-'))
    datacard.write('\n') 
    datacard.close()
