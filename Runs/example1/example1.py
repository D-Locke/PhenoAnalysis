import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir,os.path.pardir)))
import collections
from PhenoAnalysis import *

if __name__ == '__main__':
	luminosity=100								# fb^-1
	LoadEvents=500 								# how many events to load? For testing on large files
	observables=["Mmiss","PTjj"]			# which observables to compute, store and plot - check they are defined in observables.py
	process={"Njets" : 2, "Nmuons" : 1} 		# labels the required final state, here ==2 jets and ==1 muons

	rootDir='.'			# directory of event files
	args=[]				# [ name, LoadEvents, luminosity, label, type, model, process, observables, plotStyle ]

	# signals - here is Inert Doublet Model, e+e- -> DD,4*x where x is quark, muon or neutrino
	args.append([rootDir+'/IDM_signal.lhe', LoadEvents, luminosity, "eE->DDmNmjj","signal","IDM",process,observables,{'linestyle': 'dashed','color':'green'}])

	#backgrounds - here SM background e+e- -> 4*x
        args.append([rootDir+'/SM_viaWW.lhe', LoadEvents, luminosity, "eE->WW->mNmjj","background","SM",process,observables,{'linestyle': 'solid','color':'red'}])

	objects = parallel_readLHE(args)		# parse root files in parallel
	
	# define cuts here
	cuts=collections.OrderedDict()
	cuts['Mmiss']=[170,500]
	cuts['Ejj']=[0,200]

	cutNplot(objects,cuts,PlotCuts=False)

	print "Finished analysis, please see cutNplot for plots and results. Dataframe of observables is stored in /data"