from ROOT import TLorentzVector
from itertools import chain,combinations
from math import sqrt
import numpy as np
import settings

def M_miss(parts):
	# here parts is visible parts - FOR LEPTON COLLIDERS HERE!
	# p=initial[0].p4+initial[1].p4
	p=TLorentzVector(0,0,0,settings.globDict['Energy'])	# px,py,pz,E
	for part in parts:
		p=p-part.P4()
	return p.M()

def M(parts):
	p=TLorentzVector(0,0,0,0)	# px,py,pz,E
	for part in parts:
		#part.P4().Print()
		p=p+part.P4()
	return p.M()

def E(parts):
	p=TLorentzVector(0,0,0,0)	# px,py,pz,E
	for part in parts:
		#part.P4().Print()
		p=p+part.P4()
	return p.E()

def Eta(parts):
	""" psuedorapidity """
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.P4()
	return p.Eta()

def PT(parts):
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.P4()
	return p.Pt()

def DeltaEta(parts):
	if len(parts) != 2:
		print "DeltaEta only supports 2 final state particles currently"
		return -1 
	return abs(parts[0].P4().Eta() - parts[1].P4().Eta())