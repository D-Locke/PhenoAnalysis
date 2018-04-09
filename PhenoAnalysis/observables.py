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
    JET1,JET2,MUON = partList
    beamP4=TLorentzVector(0,0,0,500) # test without ISR+BS
    visibleP4=JET1.P4()+JET2.P4()+MUON.P4()
    obs={}

    # observable definitions go here
    obs["Mmiss"] = (beamP4-visibleP4).M()
    obs["Ejj"] = (JET1.P4()+JET2.P4()).E()
    obs["PTjj"] = (JET1.P4()+JET2.P4()).Pt()
    obs["PTmu"] = MUON.P4().Pt()
    obs["PTmiss"] = visibleP4.Pt()
    obs["CosThetajj"] = (JET1.P4()+JET2.P4()).CosTheta()

    #print (JET1.P4()+JET2.P4()).E()

    return obs[obsName]