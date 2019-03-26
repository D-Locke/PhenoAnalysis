import re
import keyword


def isidentifier(s):
    if s in keyword.kwlist:
        return False
    return re.match(r'^[a-z_][a-z0-9_]*$', s, re.I) is not None

class partDef():
	""" here is where to define new particle names and labels, good for builtins """
	# MAKE THIS ALSO GENERAL FOR LHE!!
	def __init__(self, name, branchName, PID, **kwargs):
		if not isidentifier(branchName):
			exit('branchName {} is either an invalid python variable name or a python keyword!'.format(branchName))

		self.name = name
		self.branchName = branchName
		self.latex = kwargs.get('latex',name)
		if 'latex' in kwargs: del kwargs['latex'] # don't look for this in ROOT!
		# attr are those which a ROOT Tobject contains...
		self.attr={}
		self.attr['PID'] = PID
		self.attr.update(kwargs) # kwargs could have e.g latex

	def __str__(self):
		string = ""#name: {}\bbranchName: {}\nPID: {}\n".format(self.name,self.branchName,self.PID)
		for k in self.__dict__:
			string+="\t{}: {}\n".format(k,self.__dict__[k])
		return string



class partDefs(dict):
	""" should also write function that attempts to generate this from either LHE or ROOT... """
	def add(self, name, branchName, PID, **kwargs):
		if name in self:
			exit('Particle name {} already used!'.format(name))
		else:
			self[name] = partDef(name, branchName, PID, **kwargs)
			

	def __str__(self):
		string='All particle definitions \n===================\n'
		for k in self:
			string += '----------------------\n'
			string += '{}\n'.format(self[k])
		return string


