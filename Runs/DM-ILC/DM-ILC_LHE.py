"""this is a minimalist ROOT file reader that will iterate over file and store requested observables
in dataframe, similar to lheAnalysis. See README"""
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir,os.path.pardir)))
from PhenoAnalysis import *

if __name__ == '__main__':
	luminosity=500
	LoadEvents=100000													# how many events to load?
	observables=["Mmiss","PTmiss","Ejj","PTjj","Emu","PTmu","CosThetajj"]			# which observables to compute, store and plot - check they are defined in ROOTreader.py!
	process={"Njets" : 2, "Nmuons" : 1} 								# labels the required final state, here ==2 jets and ==1 muons

	rootDir='/home/dan/Dropbox/Projects/DM-ILC/Analysis/events'
	args=[]				# [ name, LoadEvents, luminosity, label, type, model, process, observables, plotStyle ]

	#signals
	args.append([rootDir+'/SDM_ONSHELL.lhe', LoadEvents, luminosity, "SDM-signal","signal","I2HDM",process,observables,{'linestyle': 'dashed','color':'green'}])
	args.append([rootDir+'/FDM_ONSHELL.lhe', LoadEvents, luminosity, "FDM-signal","signal","MFDM",process,observables,{'linestyle': 'solid','color':'green'}])

	#backgrounds
	args.append([rootDir+'/SM_viaWW.lhe', LoadEvents, luminosity,"BW1","background","SM",process,observables,{'linestyle': 'solid','color':'red'}])
	args.append([rootDir+'/SDM_BW2+BW3_ONSHELL.lhe', LoadEvents, luminosity, "BW2+BW3-SDM","background","I2HDM",process,observables,{'linestyle': 'dashed','color':'orange'}])
	args.append([rootDir+'/FDM_BW2+BW3_ONSHELL.lhe', LoadEvents, luminosity, "BW2+BW3-FDM","background","MFDM",process,observables,{'linestyle': 'solid','color':'orange'}])
	args.append([rootDir+'/SM_BW4.lhe', LoadEvents, luminosity, "BW4","background","SM",process,observables,{'linestyle': 'solid','color':'yellow'}])

	objects = parallel_readLHE(args)		# parse root files in parallel
	cuts={ 	'Mmiss': [170,500],	'Ejj' : [0,200]}

	cutNplot(objects,cuts)