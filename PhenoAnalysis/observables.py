from ROOT import TLorentzVector

def M_miss(parts):
	# here parts is visible parts
	#p=initial[0].p4+initial[1].p4
	p=TLorentzVector(0,0,0,500)
	for part in parts:
		p=p-part.p4
	return p.Mag()

def PT_miss(parts):
	# here parts is visible parts
	#p=parts[0].p4-parts[0].p4
	p=TLorentzVector(0,0,0,500)
	for part in parts:
		p=p-part.p4
	return p.Pt()

def Eta(parts):
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.p4
	return p.Eta()

def E(parts):
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.p4
	return p.E()


def PT(parts):
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.p4
	return p.Pt()

def CosTheta(parts):
	p=TLorentzVector(0,0,0,0)
	for part in parts:
		p=p+part.p4
	return p.CosTheta()

# SHOULD EXTEND OBSERVABLES LIST AND MAKE COMMON TO LHEANALYSIS
def calc_obs(obsName,partList):
	""" remember to define ranges and labels in plotting.py! """
	JET1,JET2,MUON = partList

	obs={}

	obs["Mmiss"] = M_miss(partList)
	obs["PTmiss"] = PT_miss(partList)

	obs["Ejj"] = E([JET1,JET2])
	obs["PTjj"] = PT([JET1,JET2])
	obs["Etajj"] = Eta([JET1,JET2])
	obs["CosThetajj"] = CosTheta([JET1,JET2])

	obs["Emu"]= E([MUON])
	obs["PTmu"] = PT([MUON])
	obs["Etamu"] = Eta([MUON])
	obs["CosThetamu"] = CosTheta([MUON])

	return obs[obsName]