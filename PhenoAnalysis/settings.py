""" for passing around global dictionary """

def init(AnalysisName, Energy, Lumi, Procs, ObsNames, mode):
	global globDict
	globDict={  'AnalysisName':AnalysisName,
				'Energy': Energy,
				'Lumi': Lumi,
				'Procs': Procs,
				'ObsNames': ObsNames,
				'mode': mode # Custom or Builtin
				}