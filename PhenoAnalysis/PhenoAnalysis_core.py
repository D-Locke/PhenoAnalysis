import sys, os
from math import sqrt
import multiprocessing

from LHEreader import *
from ROOTreader import *
from observables import *
from plotting import *


class Logger:
    """ For logging console output to text file"""
    def __init__(self,filename):
        self.terminal = sys.stdout
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
    p = multiprocessing.Pool()
    objects = p.map(readROOT, args)
    p.close()
    p.join()
    return objects

def parallel_readLHE(args):
    """parallelizes reading of .root and storage of observables dataframe"""
    p = multiprocessing.Pool()
    objects = p.map(readLHE, args)
    p.close()
    p.join()
    return objects



def ApplyCuts(objects, observable, limits):
    """hacky way, would be better to act on event objects than this obs dataframe!"""
    low=limits[0]
    high=limits[1]
    efficiencies={}
    print observable+' cut\t'+'['+str(low)+','+str(high)+']\n'
    for obj in objects:
        before=obj.Nevents 
        obj.obs = obj.obs[obj.obs[observable]>low]
        obj.obs = obj.obs[obj.obs[observable]<high]
        # print cutObs.head()
        print "\n\n-----------------------"
        print obj.label
        after=obj.Nevents
        print "Events: "+str(after)+'/'+str(before)
        if before!=0:
            Efficiency=after/before
        else:
            Efficiency=-1
        print "Efficiency: ",str(Efficiency)
        efficiencies[obj.label]=Efficiency
    return efficiencies


def significance(s,b):
    return s/sqrt(s+b)

def cutNplot(objects, cuts):
    #events of this decay chain:
    decEvents={}
    for obj in objects:
        decEvents[obj]=obj.Nevents

    AllEff={}
    quickPlot(objects ,"NoCuts")
    Dalitz(objects ,"NoCuts")
    for i,cut in enumerate(cuts):
        print "\nAPPLYING CUT "+str(i+1)+": \n**************************"
        AllEff[cut]=ApplyCuts(objects, cut, cuts[cut])
        quickPlot(objects , cut+"Cut")
        Dalitz(objects , cut+"Cut")

    print "\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "TOTAL: \n"
    for obj in objects:
        print obj.label+': '
        totalEff=float(len(obj.obs))/decEvents[obj]
        print "\tEvents: "+str(obj.Nevents)+'/'+str(decEvents[obj])
        print "\tEfficiency: "+str(float(obj.Nevents)/decEvents[obj])
        print ""
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"

    cutEvents={}
    for obj in objects:
        cutEvents[obj.label]=obj.Nevents

    print "\nSIGNIFICANCES: "
    for obj in objects:
        if obj.type=="signal":
            BGevents=0
            BGevents=sum(bg.Nevents for bg in objects if (bg.type=="background" and (bg.model=="SM" or bg.model==obj.model)))
            if BGevents!=0:
                print obj.label+': '
                totalEff=float(obj.Nevents)/decEvents[obj]
                signif = significance(obj.Nevents,BGevents)
                print "\t\ts/sqrt(s+b): "+str(signif)
            else:
                print "No backgrounds supplied"






