import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir,os.path.pardir)))
import collections
from Modules import *
from Modules import settings

class processes:
	"""These should be defined for each analysis - preselection cuts to select 'channels'"""
	def __init__(self,proc_label):
		self.proc_label=proc_label

	def hadronic(self,event):
		if event.Jet.GetEntries() == 4:
			return True
		return False


	def preselection(self,event):
		""" see definitions in Modules/preselection.py """
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
	observables=["PTj1","Mjj","Ejj"]			# which observables to compute, store and plot - check they are defined in observables.py
	process=processes("hadronic")		#  preselection cuts for defining different channels contained within single file

	# some of this crap should go in global dict
	settings.init(AnalysisName, Energy, luminosity, process, observables, mode='Custom', BGsys=0.0, calc_s95=True)

	# Custom particle definitions - name, branchName, PID required, other kwargs may be requested (so long as ROOT leaf exists with same name)
	# lists should be given as kwargs, meaning "if X list contains branch.X"
	# parts = part.partDefs()
	# parts.add("C+","Chp", PID=[1000024],Status=[62])
	# parts.add("C-","Chm", PID=[-1000024],Status=[62])

	rootDir='.'			# directory of event files
	args=[]				# [ name, LoadEvents, luminosity, label, type, model, process, observables, plotStyle ]

	# signals - here is Inert Doublet Model, e+e- -> DD,4*x where x is quark, muon or neutrino
	args.append([rootDir+'/SIGNALEVENTS.lhe', LoadEvents, "eE->DDmNmjj","signal","BSM_MODEL_NAME",{'linestyle': 'dashed','color':'green'},recalc])

	#backgrounds - here SM background e+e- -> 4*x
	args.append([rootDir+'/BGEVENTS.lhe', LoadEvents, "eE->WW->mNmjj","background","SM",{'linestyle': 'solid','color':'red'},recalc])

	objects = parallel_readLHE(args)		# parse root files in parallel

	# define cuts here
	cuts=collections.OrderedDict()
	cuts['Ejj']=[0,200]

	# define plots
	plots=[{"label":"PTj1","binning": 30,"yscale":"log"},
		{"label":"Ejj","binning": 30,"yscale":"log"}]
	cutNplot(objects,cuts,plots,PlotCuts=True,Dalitz=False)	# will apply cuts in order, print results and calculate 1D and 2D histograms of all observables
	cornerPlot(objects, vars=observables, saveas="cornerPlot_allCuts.png")

	print "Finished analysis, see cutNplot for plots and results. Dataframe of observables is stored in /data"
