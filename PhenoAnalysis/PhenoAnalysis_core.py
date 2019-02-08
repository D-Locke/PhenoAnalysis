import sys, os
from math import sqrt
import multiprocessing

from LHEreader import *
from ROOTreader import *
from observables import *
from plotting import *
from preselection import *
import copy

"""
class RunInfo:
Should contain:
* metadata e.g name,lum,energy, lots of the things PADATA shouldn't be storing
* PAData object "pointers", stored in some structure that makes clear relationships (i.e depends on model and whether sig/bg)
* cuts, should be dataframe instead of orderedDict really
* plots with info
"""
class PAData:
    """Object containing metadata of root file, and observables dataframe"""
    def __init__(self,filetype,Nentries,LoadEvents,luminosity,Energy,label,type,model,process,plotStyle):
        self.filetype=filetype
        self.Nentries=Nentries      # this is how many events stored in full .ROOT file
        self.LoadEvents=LoadEvents # this is how many to load
        self.Energy=Energy
        self.luminosity=luminosity
        self.obs=pd.DataFrame()  # for shoving in dataframe containing observables - SHOULD INSTEAD CREATE METHODS TO HAVE OBSERVABLES IN EACH EVENT CLASS!
        self.events=[]
        self.label=label
        self.flabel=label.replace(' ', '_')
        self.type=type # e.g "signal" or "background"
        self.process=process
        self.model=model
        self.plotStyle=plotStyle
        self.ObsFilename=self.ObsFilename()


    @property
    def MCevents(self):
        """ number of MC events that are curerntly in object """
        return len(self.obs)

    @property
    def Nevents(self):
        """ for number of detector level events remaining after cuts """
        if len(self.obs) < 1:
            Nevents=0
        else:
            Nevents=sum(self.obs["EventWeight"])
        return Nevents

    @property
    def totXsec(self):
        """ total Xsec before any cuts """
        if len(self.obs) < 1:
            totXsec=0
        else:
            totXsec=self.obs["EventWeight"][0]*self.LoadEvents/(self.luminosity)
        return totXsec

    @property
    def Xsec(self):
        """ for getting Xsec after some cuts """
        if len(self.obs) < 1:
            Xsec=0
        else:
            Xsec=sum(self.obs["EventWeight"])/(self.luminosity)
        return Xsec

    def __str__(self):
        return ("\n{label} \n===========\nLoaded MC events: {events}"
            "\nProccess: {proc}"
            "\nBeam Energy: {E}GeV"
            "\nLuminosity: {lum}fb^-1"
            "\nTotal CrossSection [fb]: {totXsec}\nProcess CrossSection[fb]: {Xsec}\n"
            "MC events in proc: {MCevents}\n"
            "Observables:\n {obs}".format(label=self.label,
                                                       events=self.LoadEvents,
                                                       proc=self.process.proc_label,
                                                       E=self.Energy,                                            
                                                       lum=self.luminosity,
                                                       totXsec=self.totXsec,
                                                       Xsec=self.Xsec,
                                                       MCevents=self.MCevents,
                                                       obs=self.obs.head()))
    def ObsFilename(self):
        return './data/'+self.flabel+'_'+str(self.LoadEvents)+'_obs_'+str(self.filetype)+'.dat.gz'

    def saveObs(self):
        self.obs.to_csv(self.ObsFilename, compression='gzip', sep='\t',index=False)

    def readObs(self, **kwargs):
        
        if 'Nrows' in kwargs:
            print "\nDataframe already stored, loading first {} events from {file} ...\n".format(kwargs['Nrows'],file=kwargs['datFilename'])
            self.obs=pd.read_csv(kwargs['datFilename'], compression='gzip',sep='\t', nrows=kwargs['Nrows'])        
        else:
            print "\nDataframe already stored, loading {file} ...\n".format(file=self.ObsFilename)
            self.obs=pd.read_csv(self.ObsFilename, compression='gzip',sep='\t')

    def getBackgrounds(self,objects):
        """ Given a list of objects, return those that are backgrounds for given signal """
        bg_objects=[]
        if self.type=="signal":
            for obj in objects:
                if (obj.type=="background" and (obj.model=="SM" or obj.model==self.model)):
                    bg_objects.append(obj)
        return bg_objects

    def getTotalBackgroundEvents(self,objects):
        bg_objects = self.getBackgrounds(objects)
        return sum(bg.Nevents for bg in bg_objects)



class Logger:
    """ For logging console output to text file"""
    def __init__(self,filename):
        self.terminal = sys.stdout
        open(filename, 'w').close() #clear previous run
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

def parallel_readROOT(args):
    """parallelizes reading of .root and storage of observables dataframe"""
    sys.stdout = Logger("./cutNplot/ROOT/RUN_INFO.log")
    p = multiprocessing.Pool()
    objects = p.map(readROOT, args)
    p.close()
    p.join()
    for obj in objects:
        print obj
    return objects

# def parallel_readLHE(args):
#     return [readLHE(args[0]),readLHE(args[1])]

def parallel_readLHE(args):
    """parallelizes reading of .root and storage of observables dataframe"""
    sys.stdout = Logger("./cutNplot/LHE/RUN_INFO.log")
    p = multiprocessing.Pool()
    objects = p.map(readLHE, args)
    p.close()
    p.join()
    for obj in objects:
        print obj
    return objects

def printCutHeader(objects):
    """ produce latex tables with pandas df.to_latex()!!"""
    tablefiledat = './cutNplot/{}/cutflow_table.dat'.format(objects[0].filetype)
    with open(tablefiledat, 'w') as f:
        f.write('Cut\tLower\tUpper')
        for obj in objects:
            f.write('\t{}'.format(obj.label))
            if obj.type=="signal":
                f.write('\t{0} ({3})\t{1} ({3})\t{2} ({3})'.format('Total BG','S/B','Z',obj.model))
        f.write(' \n')

def printCutRow(objects, observable, limits):
    tablefiledat = './cutNplot/{}/cutflow_table.dat'.format(objects[0].filetype)
    with open(tablefiledat, 'a') as f:
        f.write('{}\t{}\t{}'.format(observable,limits[0],limits[1]))
        for obj in objects:
            f.write('\t{}'.format(obj.Nevents))
            if obj.type=="signal":
                totBG=obj.getTotalBackgroundEvents(objects)
                if totBG>0.0:
                    SoverB=obj.Nevents/totBG
                    Signif=significance(obj.Nevents,totBG)
                else:
                    SoverB, Signif = -1, -1
                f.write('\t{}\t{}\t{}'.format(totBG,SoverB,Signif))

        f.write('\n')


def ApplyCut(objects, observable, limits):
    """hacky way, would be better to act on event objects than this obs dataframe?"""
    low=limits[0]
    high=limits[1]
    Efficiency=-1

    for obj in objects:
        obj.before=obj.Nevents
        if observable!="NoCuts": 
            obj.obs = obj.obs[obj.obs[observable]>low]
            obj.obs = obj.obs[obj.obs[observable]<high]

    print observable+' cut\t'+'['+str(low)+','+str(high)+']\n'
    for obj in objects:
        print "\n\n"
        print "\t"+str(obj.label)
        print "\t-----------------------"
        print "\tXsec [fb] : "+str(obj.Nevents/obj.luminosity)+'/'+str(obj.before/obj.luminosity)
        if obj.before!=0:
            Efficiency=obj.Nevents/obj.before
        print "\tEfficiency: ",str(Efficiency)
        if obj.type=="signal":
            BGevents=obj.getTotalBackgroundEvents(objects)
            if BGevents!=0:
                print "\ts/b: "+str(int(obj.Nevents))+" / "+str(int(BGevents))  
                print "\ts/b: "+str(float(obj.Nevents)/BGevents)
                print "\ts/sqrt(s+b): "+str(significance(obj.Nevents,BGevents))
            else:
                "\tZero background events remain!"
    printCutRow(objects, observable, limits)


def significance(s,b):
    return s/sqrt(s+b)

def EmuOutput(objects, cuts,nbins):
    decEvents={}
    for obj in objects:
        decEvents[obj.label]=obj.Nevents

    for obj in objects:
        print obj.label, obj.MCevents
    for i,cut in enumerate(cuts):
        print "\nAPPLYING CUT "+str(i+1)+": \n**************************"
        ApplyCut(objects, cut, cuts[cut])
    EmuPlot(objects,nbins)
    printInfo(decEvents,objects)


def plotCutEffects(object,cuts,plots,**kwargs):
    objects=[copy.deepcopy(object) for cut in cuts]
    for obj,cut in zip(objects,cuts):
        ApplyCut([obj],cut,cuts[cut])
        obj.label=obj.label+" Cut:"+cut

    #set colors
    cmap = plt.get_cmap('jet')
    colors = cmap(np.linspace(0, 1.0, len(objects)))

    for i,obj in enumerate(objects):
        obj.plotStyle={'linestyle': 'dashed','color':colors[i]}
        #print obj
    #objects=[copy.deepcopy(object) for cut in cuts]
    objects=[object]+objects
    HistPlot(objects ,plots,"CutEffects")


def cutNplot(objects, cuts,plots,**kwargs):
    PlotCuts=kwargs.get('PlotCuts',False)
    PlotDalitz=kwargs.get('Dalitz',False)
    printCutHeader(objects)

    decEvents={}
    for obj in objects:
        decEvents[obj.label]=obj.Nevents

    print "\nAPPLYING CUT 0: \n**************************"
    ApplyCut(objects,"NoCuts",[0,0])
    HistPlot(objects ,plots,"NoCuts")
    HistPlot(objects ,plots,"NoCuts_showCuts",showCuts=True,cuts=cuts)
    if PlotDalitz: Dalitz(objects ,plots,"NoCuts")

    for i,cut in enumerate(cuts):
        print "\nAPPLYING CUT "+str(i+1)+": \n**************************"
        ApplyCut(objects, cut, cuts[cut])
        if PlotCuts==True or i==len(cuts)-1:
            HistPlot(objects, plots, cut+"Cut")
            if PlotDalitz: Dalitz(objects, plots, cut+"Cut")

    # print final plots with all cuts applied
    HistPlot(objects ,plots,"AllCuts")
    if PlotDalitz: Dalitz(objects ,plots,"All`Cuts")
    # EmuPlot(objects)
    #CompPlot(objects , "AllCuts")

    print "\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "TOTALS: \n"
    for obj in objects:
        print obj.label+': '
        totalEff=float(len(obj.obs))/decEvents[obj.label]
        print "\tEvents: "+str(obj.Nevents)+'/'+str(decEvents[obj.label])
        print "\tEfficiency:"+str(float(obj.Nevents)/decEvents[obj.label])
        print ""
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"

    cutEvents={}
    for obj in objects:
        cutEvents[obj.label]=obj.Nevents

    printInfo(decEvents,objects)



def printInfo(decEvents,objects):
    print "\n############################################################"
    print "\nTOTAL SIGNIFICANCES: "
    for obj in objects:
        if obj.type=="signal":
            BGevents=0
            decBGevents=sum(decEvents[bg.label] for bg in objects if (bg.type=="background" and (bg.model=="SM" or bg.model==obj.model)))
            BGevents=sum(bg.Nevents for bg in objects if (bg.type=="background" and (bg.model=="SM" or bg.model==obj.model)))
            if BGevents!=0:
                print obj.label+': '
                print "\t\tSignal efficiency: "+str(float(obj.Nevents)/decEvents[obj.label])
                print "\t\tTotal Background efficiency: "+str(float(BGevents)/decBGevents)
                print "\t\ts/b: "+str(float(obj.Nevents)/BGevents)
                print "\t\ts/sqrt(s+b): "+str(significance(obj.Nevents,BGevents))
            else:
                print "\t\tZero background events remain!"
    print "\n############################################################\n"




