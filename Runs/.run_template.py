import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir,os.path.pardir)))
from PhenoAnalysis import *

if __name__ == '__main__':
	luminosity=500
	LoadEvents=100000 													# how many events to load?
	observables=["Mmiss","Ejj","PTmu","PTmiss","CosThetajj"]			# which observables to compute, store and plot - check they are defined in ROOTreader.py!
	process={"Njets" : 2, "Nmuons" : 1} 								# labels the required final state, here >=2 jets and ==1 muons

	rootDir='/home/dan/Dropbox/Projects/DM-ILC/Analysis/events'
	args=[]				# [ name, LoadEvents, luminosity, label, type, model, process, observables, plotStyle ]

	# signals
	args.append([rootDir+'/FILE1.lhe', LoadEvents, luminosity, "LABEL1","signal","MODEL1",process,observables,{'linestyle': 'dashed','color':'green'}])

	#backgrounds
	args.append([rootDir+'/FILE2.lhe', LoadEvents, luminosity,"LABEL2","background","SM",process,observables,{'linestyle': 'solid','color':'red'}])

	objects = parallel_readLHE(args)		# parse root files in parallel
	cuts={ 	'Mmiss': [170,500],	'Ejj' : [0,200]}

	cutNplot(objects,cuts)
