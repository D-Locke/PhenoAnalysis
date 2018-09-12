import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir,os.path.pardir)))
import collections
from PhenoAnalysis import *

class processes:
	"""These should be defined for each analysis - preselection cuts to select 'channels'"""
	def __init__(self,proc_label):
		self.proc_label=proc_label

	def semi_lept(self,event):
		""" for final states containing 1 muon and a dijet"""
		if len(event.Muon)== 1 and len(event.Jet) == 2:# or (event.Jet.GetEntries() > process["Njets"] and event.Jet.At(2).P4().Pt()<10): # allow soft jets
			return True
		return False

	def lept(self,event):
		""" for final states containing 2 muons """		
		if len(event.Muon) == 2 and len(event.Jet) == 0:
			if event.Muon.At(0).Charge == -1*event.Muon.At(1).Charge:
				return True
		return False

	def hadr(self,event):
		if len(event.Muon) == 0 and len(event.Jet) == 4:
			return True
		return False


	def preselection(self,event):
		""" see definitions in PhenoAnalysis/preselection.py """
		#filterPhaseSpace(event.Electron, 20, -2.47, 2.47)
		#filterPhaseSpace(event.Muon, 20, -3.0, 3.0)
		#filterPhaseSpace(event.Jet, 20, -3.0, 3.0)
		#overlapRemoval(event.Jet,event.Electron,0.2)
		#overlapRemoval_2(event.Electron,event.Jet,0.2,0.4)
		#overlapRemoval_jm(event.Muon, event.Jet, event.Track,deltaR=0.5,matchingTracks=3)
		return 0

	def selection(self,event):
		if self.proc_label=="semi-leptonic":
			return self.semi_lept(event)
		if self.proc_label=="hadronic":
			return self.hadr(event)
		if self.proc_label=="leptonic":
			return self.lept(event)
		else:
			return False

if __name__ == '__main__':
	Energy = 500								# TeV
	luminosity=100								# fb^-1
	LoadEvents=500 								# how many events to load? For testing on large files
	recalc=True									# if dataframe of observables already stored, recalculate and overwrite if True.
	observables=["Mmiss","Ejj"]			# which observables to compute, store and plot - check they are defined in observables.py
	process=processes("semi-leptonic")		#  preselection cuts for defining different channels contained within single file

	rootDir='.'			# directory of event files
	args=[]				# [ name, LoadEvents, luminosity, label, type, model, process, observables, plotStyle ]

	# signals - here is Inert Doublet Model, e+e- -> DD,4*x where x is quark, muon or neutrino
	args.append([rootDir+'/IDM_signal.lhe', LoadEvents, luminosity, Energy, "eE->DDmNmjj","signal","IDM",process,observables,{'linestyle': 'dashed','color':'green'},recalc])

	#backgrounds - here SM background e+e- -> 4*x
	args.append([rootDir+'/SM_viaWW.lhe', LoadEvents, luminosity, Energy, "eE->WW->mNmjj","background","SM",process,observables,{'linestyle': 'solid','color':'red'},recalc])

	objects = parallel_readLHE(args)		# parse root files in parallel
	
	# define cuts here
	cuts=collections.OrderedDict()
	cuts['Mmiss']=[170,500]
	cuts['Ejj']=[0,200]

	# define plots
	plots=[{"label":"Mmiss","binning": 30,"yscale":"log"},{"label":"Ejj","binning": 30,"yscale":"log"}]
	cutNplot(objects,cuts,plots,PlotCuts=True,Dalitz=False)	# will apply cuts in order, print results and calculate 1D and 2D histograms of all observables

	print "Finished analysis, see cutNplot for plots and results. Dataframe of observables is stored in /data"

	results=pd.read_csv('cutNplot/LHE/cutflow_table.dat',sep='\t')
	print '\nFrom cutNplot/LHE/cutflow_table.dat \n======================='
	print results
