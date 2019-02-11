import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir,os.path.pardir)))
import collections
from PhenoAnalysis import *
from PhenoAnalysis import settings

class processes:
	"""These should be defined for each analysis - preselection cuts to select 'channels'"""
	def __init__(self,proc_label):
		self.proc_label=proc_label

	def semi_lept(self,event):
		if event.Jet.GetEntries() == 2 and event.Muon.GetEntries() == 1:
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
		return getattr(self, self.proc_label)(event)

if __name__ == '__main__':
	AnalysisName = "example1_tests"
	Energy = 500								# TeV
	luminosity=100								# fb^-1
	LoadEvents=1000 								# how many events to load? For testing on large files
	recalc=True									# if dataframe of observables already stored, recalculate and overwrite if True.
	observables=["PTj1", "Ejj"]			# which observables to compute, store and plot - check they are defined in observables.py
	process=processes("semi_lept")		#  preselection cuts for defining different channels contained within single file

	# some of this crap should go in global dict
	settings.init(AnalysisName, Energy, luminosity, process, observables, mode='Custom', BGsys=0.1, calc_s95=True)

	rootDir='.'			# directory of event files
	args=[]				# [ name, LoadEvents, luminosity, label, type, model, process, observables, plotStyle ]

	#backgrounds - here SM background e+e- -> 4*x
	args.append([rootDir+'/SM_viaWW.root', LoadEvents, "eE->WW->mNmjj","background","SM",{'linestyle': 'solid','color':'red'},recalc])

	#objects = parallel_readROOT(args)		# parse root files in parallel
	object0 = readROOT(args[0])
	objects=[object0]

	# define cuts here
	cuts=collections.OrderedDict()
	cuts['Ejj']=[0,200]

	# define plots
	plots=[{"label":"PTj1","binning": 30,"range":[0,500.0],"yscale":"log"},
		{"label":"Ejj","binning": 30,"range":[0,500.0],"yscale":"log"}]
	cutNplot(objects,cuts,plots,PlotCuts=True,Dalitz=False)	# will apply cuts in order, print results and calculate 1D and 2D histograms of all observables
	cornerPlot(objects, vars=observables, saveas="cornerPlot_allCuts.png")

	print "Finished analysis, see cutNplot for plots and results. Dataframe of observables is stored in /data"


