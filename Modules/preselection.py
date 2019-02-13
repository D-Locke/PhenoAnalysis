def countMatchingTracks(tracks, jet, minpt):
    ntracks = 0
    for track in tracks:
        if jet.P4().DeltaR(track.P4()) < 0.4 and (track.PT > minpt or minpt==-1.0):
            ntracks+=1
    return ntracks

def overlapRemoval(candidates,neighbours,dR,psuedorapidity="eta"):
    if neighbours.GetEntries()==0: return candidates
    for candidate in candidates:
        for neighbour in neighbours:
            if psuedorapidity=="eta":
                if candidate.P4().DeltaR(neighbour.P4()) < dR:
                    candidates.RecursiveRemove(candidates)
            #if psuedorapidity=="y":
                # dont need atm
    #return candidates

def overlapRemoval_2(candidates, neighbours, dR1, dR2):
    if neighbours.GetEntries() == 0: return candidates
    for candidate in candidates:
        for neighbour in neighbours:
            dR = candidate.P4().DeltaR(neighbour.P4())
            if (dR1<dR and dR<dR2):
                candidates.RecursiveRemove(candidate)
    #return candidates

def overlapRemoval_jm(muons,jets,tracks,deltaR,matchingTracks):
    for muon in muons:
        for jet in jets:
            if muon.P4().DeltaR(jet.P4()) < deltaR:
                # if muon in jet cone
                if countMatchingTracks(tracks, jet, deltaR) >= matchingTracks:
                    muons.RecursiveRemove(muon)
                else:
                    jets.RecursiveRemove(jet)
                return True
            else:
                return False

def filterPhaseSpace(objects,pt,etamin,etamax):
    """ quick filter for pt and upper/lower eta cuts """
    for obj in objects:
        if obj.PT < 20 or (obj.Eta < etamin and obj.Eta > etamax):
            objects.RecursiveRemove(obj)

def dPhi(jets, missingET):
    dphimi=0
    for i,jet in enumerate(jets):
        #for first jet
        if i==0: dphimin = abs(jet.P4().DeltaPhi(missingET.P4()))
        else: dphimin = min(jet.P4().DeltaPhi(missingET.P4()),dphimin)
    return dphimin


def dropSoft(object,E):
	for j in object:
		if j.P4().E()<E:	# E in GeV as usual
			object.RecursiveRemove(j)

def keepLeading(parts,N):
	""" remove subleading parts (sorted by default()"""
	parts.RemoveRange(N, parts.GetEntries()-1)