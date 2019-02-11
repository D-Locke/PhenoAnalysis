""" for passing around global dictionary """

def init(AnalysisName, Energy, Lumi, Procs, ObsNames, mode, **kwargs):
	global globDict
	globDict={  'AnalysisName':AnalysisName,
				'Energy': Energy,
				'Lumi': Lumi,
				'Procs': Procs,
				'ObsNames': ObsNames,
				'mode': mode, # Custom or Builtin
				'sys' : kwargs.get('sys',0.0),
				'calc_s95' : kwargs.get('calc_s95',False)
				}

