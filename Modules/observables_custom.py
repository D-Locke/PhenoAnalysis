from ROOT import TLorentzVector
from itertools import chain,combinations
from math import sqrt
import numpy as np

"""
In future create obsevable class, should contain:
* observable name
* plot label
* plot range
* binning (at least for 1D) - take either integer which will produce uniform binning, or arbitrary positions e.g [0, 12, 51, 211, 300]
* maybe even allow function call with e.g "E(j1,j2)" - use getattr() and split for this
"""
def M_miss(Energy,parts):
	# here parts is visible parts
	#p=initial[0].p4+initial[1].p4
	p=TLorentzVector(0,0,0,Energy)	# px,py,pz,E
	for part in parts:
		p=p-part.P4()
	return p.M()

def M(parts):
	p=TLorentzVector(0,0,0,0)	# px,py,pz,E
	for part in parts:
		#part.P4().Print()
		p=p+part.P4()
	return p.M()

def M_jj(parts):
	""" find pair of jets with invar mass closest to MW """
	MW=80.385
	p=TLorentzVector(0,0,0,0)	# px,py,pz,E
	Mjets=100000

	for j1,j2 in combinations(parts,2):
		if (abs((j1.P4()+j2.P4()).M()-MW) < abs(Mjets-MW)):
			Mjets=(j1.P4()+j2.P4()).M()
	return Mjets

def deltaPhi_jj_mu(muon,jets):
	MW=80.385
	p=TLorentzVector(0,0,0,0)	# px,py,pz,E
	Mjets=100000

	# find dijets - hacky
	for j1,j2 in combinations(jets,2):
		if (abs((j1.P4()+j2.P4()).M()-MW) < abs(Mjets-MW)):
			P4jets=(j1.P4()+j2.P4())

	return muon.At(0).P4().DeltaPhi(P4jets)


def deltaR_min(p1s,p2s):
	deltaR=400
	for p1 in p1s:
		for p2 in p2s:
			if p1.P4().DeltaR(p2.P4()) < deltaR:
				deltaR = p1.P4().DeltaR(p2.P4())
	return deltaR

def p_nu_z(muon,PTmiss_vect,Mjj):
	""" calculate neutrino z momentum from solving quadratic. Know p_nu_T from pTmiss, for SM semileptonic BG and know mass is zero """

	muon=muon[0].P4()
	MW   = 80.385#Mjj # or shoud be Mjj
	#print Mjj
	M_mu = 0.1057
	M_nu = 0

	E_mu, p_mu_x, p_mu_y, p_mu_z = muon.E(), muon.Px(), muon.Py(), muon.Pz()
	p_nu_x,p_nu_y=PTmiss_vect
	alpha=(MW**2-M_nu**2-M_mu**2)/2 - (p_nu_x*p_mu_x + p_nu_y*p_mu_y)
	p_nu_T = sqrt(p_nu_x**2+p_nu_y**2)
	#print "muon: {}, {}, {}, {}".format(muon.E(), muon.Px(), muon.Py(), muon.Pz())
	#print "p_nu_T^2*(p_mu_z^2-E_mu^2)= {}".format(p_nu_T**2*(p_mu_z**2-E_mu**2))
	#print "alpha^2= {}".format(alpha**2)
	# if solution complex then assume piece inside sqrt()~0
	if p_nu_T**2*(p_mu_z**2-E_mu**2) + alpha**2 <= 0:
		#print "complex p_nu_z, setting to zero"
		p_nu_z_p, p_nu_z_m = p_mu_z*alpha/ (E_mu**2 - p_mu_z**2 ),p_mu_z*alpha/ (E_mu**2 - p_mu_z**2 )
	else:
		p_nu_z_p = ( p_mu_z*alpha + sqrt( -(p_nu_T**2)*E_mu**4 + E_mu**2*p_nu_T**2*p_mu_z**2 + E_mu**2*alpha**2 ) ) / (E_mu**2 - p_mu_z**2 ) 
		p_nu_z_m = ( p_mu_z*alpha - sqrt( -(p_nu_T**2)*E_mu**4 + E_mu**2*p_nu_T**2*p_mu_z**2 + E_mu**2*alpha**2 ) ) / (E_mu**2 - p_mu_z**2 )
		#print "p_nu_z_minus= {}".format(p_nu_z_m)
		#print "p_nu_z_plus= {}".format(p_nu_z_p)
	return p_nu_z_p, p_nu_z_m

def M_miss_pm(Energy,parts,p_nu_z,PTmiss_vect):
	p_nu_x,p_nu_y=PTmiss_vect
	p_nu_T = sqrt(p_nu_x**2+p_nu_y**2)
	E_nu = sqrt(p_nu_T**2 + p_nu_z**2)
	neutr=TLorentzVector(p_nu_x,p_nu_y,p_nu_z,E_nu)
	p=TLorentzVector(0,0,0,Energy)	# px,py,pz,E
	for part in parts:
		p=p-part.P4()
	p=p-neutr
	return p.Mag()

def PTmiss_vect(Energy,parts):
	# here parts is visible parts
	#p=parts[0].p4-parts[0].p4
	p=TLorentzVector(0,0,0,Energy)
	for part in parts:
		p=p-part.P4()
	return p.Px(),p.Py()

def PT_miss(Energy,parts):
	# here parts is visible parts
	#p=parts[0].p4-parts[0].p4
	p=TLorentzVector(0,0,0,Energy)
	for part in parts:
		p=p-part.P4()
	return p.Pt()

def Eta(parts):
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.P4()
	return p.Eta()

def E(parts):
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.P4()
	return p.E()


def PT(parts):
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.P4()
	return p.Pt()

def CosTheta(parts):
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.P4()
	return p.CosTheta()

def Sum_CosTheta(parts):
	return sum([abs(p.P4().CosTheta()) for p in parts])

# def P_DD(Energy,parts):
# 	""" P(dm,dm)^2 = (E - P(W,W))^2"""
# 	p=TLorentzVector(0,0,0,Energy)
# 	Pww=sum([part.P4() for part in parts])
# 	P_DD = (p-Pww).Mag()
# 	return P_DD


# SHOULD EXTEND OBSERVABLES LIST AND MAKE COMMON TO LHEANALYSIS
def calc_obs(Energy,obsName,event,process):
	""" calculate custom functions - most flexible way """
	""" remember to define ranges and labels in plotting.py! """

	if obsName=="Mmiss":	return M_miss(Energy, chain(event.Jet,event.Muon))
	elif obsName=="P_WW":	return M_miss(0, event.Jet)		
	elif obsName=="Ejj": return E(event.Jet)
	elif obsName=="CosThetajj": return CosTheta(event.Jet)
	elif obsName=="Evis": return E(chain(event.Jet,event.Muon))
	elif obsName=="Ejets": return E(event.Jet)

	elif obsName=="Mjets": return M(event.Jet)
	elif obsName=="Mjj": return M_jj(event.Jet)
	elif obsName=="deltaR_Jmu_min": return deltaR_min(event.Muon,event.Jet)
	elif obsName=="deltaPhi_jj_mu": return deltaPhi_jj_mu(event.Muon,event.Jet)
	elif obsName=="Mmiss_p":
		Mjj=M_miss(0,event.Jet)
		PTmiss_vec=PTmiss_vect(Energy,chain(event.Jet,event.Muon))
		p_nu_z_p,p_nu_z_m =p_nu_z(event.Muon,PTmiss_vec,Mjj)
		return M_miss_pm(Energy,chain(event.Jet,event.Muon),p_nu_z_p,PTmiss_vec)
	elif obsName=="Mmiss_m":
		Mjj=M_miss(0,event.Jet)
		PTmiss_vec=PTmiss_vect(Energy,chain(event.Jet,event.Muon))
		p_nu_z_p,p_nu_z_m =p_nu_z(event.Muon,PTmiss_vec,Mjj)
		return M_miss_pm(Energy,chain(event.Jet,event.Muon),p_nu_z_m,PTmiss_vec)
	elif obsName=="PTmiss": return PT_miss(Energy,chain(event.Jet,event.Muon))
	elif obsName=="PTjj": return PT(event.Jet)
	elif obsName=="Etajj": return Eta(event.Jet)
	elif obsName=="Emu": return E(event.Muon)
	elif obsName=="PTmu": return PT(event.Muon)
	elif obsName=="Etamu": return Eta(event.Muon)
	elif obsName=="CosThetamu": return CosTheta(event.Muon)
	elif obsName=="Tracks": event.Track.GetEntries()
	elif obsName=="Sum_CosTheta": return Sum_CosTheta(chain(event.Jet,event.Muon))
	
	# JetMatching tests ( ONLY WORK FOR ROOT ATM )

	# elif obsName=="Nj": return event.GenJet_size
	# elif obsName=="PTj1": 
	# 	if event.GenJet_size>=1:
	# 		return event.GenJet[0].PT
	# 	else: return np.nan
	# elif obsName=="PTj2":
	# 	if event.GenJet_size>=2:
	# 		return event.GenJet[1].PT
	# 	else: return np.nan

	# LHE VERSIONS FOR MWTC STUDY
	elif obsName=="Nj": 
		return len(event.Jet)
	elif obsName=="PTj1":
		return event.Jet[0].PT
	elif obsName=="PTj2": 
		return event.Jet[1].PT
	elif obsName=="deltaEta":
		return abs( event.TaggedJet[0].Eta - event.TaggedJet[1].Eta )
	elif obsName=="PTWp":
		return event.getParticlesByIDs([24])[0].PT
	elif obsName=="EtaWp":
		return event.getParticlesByIDs([24])[0].Eta
	elif obsName=="PTWm":
		return event.getParticlesByIDs([-24])[0].PT
	elif obsName=="EtaWm":
		return event.getParticlesByIDs([-24])[0].Eta
	elif obsName=="PT_WW": 
		return PT(event.Ws)
	elif obsName=="PT_jj": 
		return PT(event.TaggedJet)
	elif obsName=="MWW":
		return M(event.Ws)
	elif obsName=="MWWj1j2":
		return M(event.Ws+event.Jet)
	elif obsName=="Ej1":
		return event.Jet[0].E
	elif obsName=="Ej2":
		return event.Jet[1].E
	elif obsName=="eta_j1":
		return event.Jet[0].Eta
	elif obsName=="eta_j2":
		return event.Jet[1].Eta





	else: exit('Observable {} not found!'.format(obsName))



	# if process=="hadronic":
	# 	if obsName=="Mmiss":	return M_miss(Energy, event.Jet)
	# 	elif obsName=="P_WW":	return M_miss(0, event.Jet)		
	# 	elif obsName=="Ejj": return E(event.Jet)
	# 	elif obsName=="CosThetajj": return CosTheta(event.Jet)
	# 	else: exit('Observable {} not found!'.format(obsName))


	# if process=="semi-leptonic":
	# 	if obsName=="Mmiss": return M_miss(Energy, chain(event.Jet,event.Muon))
	# 	elif obsName=="Evis": return E(chain(event.Jet,event.Muon))
	# 	elif obsName=="Ejets": return E(event.Jet)
	# 	elif obsName=="Mjets": return M(event.Jet)
	# 	elif obsName=="Mjj": return M_miss(0,event.Jet)
	# 	elif obsName=="Mmiss_p":
	# 		Mjj=M_miss(0,event.Jet)
	# 		PTmiss_vec=PTmiss_vect(Energy,chain(event.Jet,event.Muon))
	# 		p_nu_z_p,p_nu_z_m =p_nu_z(event.Muon,PTmiss_vec,Mjj)
	# 		return M_miss_pm(Energy,chain(event.Jet,event.Muon),p_nu_z_p,PTmiss_vec)
	# 	elif obsName=="Mmiss_m":
	# 		Mjj=M_miss(0,event.Jet)
	# 		PTmiss_vec=PTmiss_vect(Energy,chain(event.Jet,event.Muon))
	# 		p_nu_z_p,p_nu_z_m =p_nu_z(event.Muon,PTmiss_vec,Mjj)
	# 		return M_miss_pm(Energy,chain(event.Jet,event.Muon),p_nu_z_m,PTmiss_vec)
	# 	elif obsName=="PTmiss": return PT_miss(Energy,chain(event.Jet,event.Muon))
	# 	elif obsName=="Ejj": return E(event.Jet)
	# 	elif obsName=="PTjj": return PT(event.Jet)
	# 	elif obsName=="Etajj": return Eta(event.Jet)
	# 	elif obsName=="CosThetajj": return CosTheta(event.Jet)
	# 	elif obsName=="Emu": return E(event.Muon)
	# 	elif obsName=="PTmu": return PT(event.Muon)
	# 	elif obsName=="Etamu": return Eta(event.Muon)
	# 	elif obsName=="CosThetamu": return CosTheta(event.Muon)
	# 	elif obsName=="Tracks": event.Track.GetEntries()
	# 	elif obsName=="Sum_CosTheta": return Sum_CosTheta(chain(event.Jet,event.Muon))
	# 	else: exit('Observable {} not found!'.format(obsName))


	# if process=="leptonic":
	# 	if obsName=="Mmiss": return M_miss(Energy, event.Muon)
	# 	elif obsName=="PTmiss": return PT_miss(Energy,event.Muon)
	# 	elif obsName=="Emu": return [E([muon]) for muon in event.Muon] 
	# 	elif obsName=="PTmu": return [PT([muon]) for muon in event.Muon] 
	# 	elif obsName=="Etamu": return [Eta([muon]) for muon in event.Muon] 
	# 	elif obsName=="CosThetamu": return [CosTheta([muon]) for muon in event.Muon]
	# 	else: exit('Observable {} not found!'.format(obsName))

