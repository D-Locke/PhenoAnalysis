from ROOT import TLorentzVector
from itertools import chain
from math import sqrt

def M_miss(Energy,parts):
	# here parts is visible parts
	#p=initial[0].p4+initial[1].p4
	p=TLorentzVector(0,0,0,Energy)	# px,py,pz,E
	for part in parts:
		p=p-part.P4()
	return p.Mag()

def M(parts):
	p=TLorentzVector(0,0,0,0)	# px,py,pz,E
	for part in parts:
		p=p+part.P4()
	return p.M()
	
def p_nu_z(muon,PTmiss_vect,Mjj):

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
	""" remember to define ranges and labels in plotting.py! """

	# CURRENTLY CALCULATING ALL- FIX THIS SO ONLY REQUESTED ARE CALCULATED!!!
	#HADRONIC
	###########
	if process=="hadronic":
		if obsName=="Mmiss":	return M_miss(Energy, event.Jet)
		elif obsName=="P_WW":	return M_miss(0, event.Jet)		
		elif obsName=="Ejj": return E(event.Jet)
		elif obsName=="CosThetajj": return CosTheta(event.Jet)
		else: exit('Observable {} not found!'.format(obsName))


	# SEMI LEPTONIC
	if process=="semi-leptonic":
		if obsName=="Mmiss": return M_miss(Energy, chain(event.Jet,event.Muon))
		elif obsName=="Mjets": return M(event.Jet)
		elif obsName=="Mjj": return M_miss(0,event.Jet)
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
		elif obsName=="Ejj": return E(event.Jet)
		elif obsName=="PTjj": return PT(event.Jet)
		elif obsName=="Etajj": return Eta(event.Jet)
		elif obsName=="CosThetajj": return CosTheta(event.Jet)
		elif obsName=="Emu": return E(event.Muon)
		elif obsName=="PTmu": return PT(event.Muon)
		elif obsName=="Etamu": return Eta(event.Muon)
		elif obsName=="CosThetamu": return CosTheta(event.Muon)
		elif obsName=="Tracks": event.Track.GetEntries()
		elif obsName=="Sum_CosTheta": return Sum_CosTheta(chain(event.Jet,event.Muon))
		else: exit('Observable {} not found!'.format(obsName))


	#LEPTONIC
	if process=="leptonic":
		if obsName=="Mmiss": return M_miss(Energy, event.Muon)
		elif obsName=="PTmiss": return PT_miss(Energy,event.Muon)
		elif obsName=="Emu": return [E([muon]) for muon in event.Muon] 
		elif obsName=="PTmu": return [PT([muon]) for muon in event.Muon] 
		elif obsName=="Etamu": return [Eta([muon]) for muon in event.Muon] 
		elif obsName=="CosThetamu": return [CosTheta([muon]) for muon in event.Muon]
		else: exit('Observable {} not found!'.format(obsName))

