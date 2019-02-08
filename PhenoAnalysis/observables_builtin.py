import KinFuncs

"""
In future create obsevable class, should contain:
* observable name
* plot label
* plot range
* binning (at least for 1D) - take either integer which will produce uniform binning, or arbitrary positions e.g [0, 12, 51, 211, 300]
* maybe even allow function call with e.g "E(j1,j2)" - use getattr() and split for this
* should also provide map from part name to pdg id (use Calchep conventions)
* not all particles are compatible with ROOT!
"""


def mysplit(str):
	""" splits number at end of string """
        head = str.rstrip('0123456789')
        tail = str[len(head):]
        if not tail:	
        	# if empty then use leading particle
        	tail=1
        return head, int(tail)


def branchName(name):
	""" Should probably read this from SLHA or something - think about how should work with arbitrary ROOT tree structures"""
	if name=="j":
		return "Jet"
	if name=="m" or name=="M":
		return "Muon"
	if name=="W+":
		return "Wp"
	if name=="W-":
		return "Wm"

class Observable:
	""" Observables - should also add plotting info as kwargs """
	def __init__(self,label):
		self.label=label
		self.latex=self.genLatex()
		self.funcName = label.split('(')[0]
		self.partNames = label.split('(')[1].split(')')[0].split(',')
		self.Parts = [mysplit(s) for s in self.partNames]

	def __str__(self):
		print self.label, self.funcName, self.partNames, self.Parts

	def genLatex(self):
		""" each func should also be a class with latex def? """
		return "tests"

	def calc(self, event):
		# put all raw observable functions in module KinFuncs
		parts=[]
		for name,order in self.Parts:
			parts.append( getattr(event, branchName(name) )[order-1] )

		return getattr(KinFuncs, self.funcName)(parts) #when use import KinFuncs




# # SHOULD EXTEND OBSERVABLES LIST AND MAKE COMMON TO LHEANALYSIS
# def calc_obs(obsName,event):
# 	funcName = obsName.split('(')[0]
# 	partNames = obsName.split('(')[1].split(')')[0].split(',')

# 	# partLists in LHE/ROOTreader should also be assigned label? (e.g "j" for )

# 	print funcName
# 	print partNames


# calc_obs(100.0,"M(j1,j2)","k")