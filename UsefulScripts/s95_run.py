import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from Modules import get_s95 as s95
from math import sqrt

totBG=8000.0
syst=0.1

S95 = s95.find_s95_exp(totBG,totBG,syst*totBG)

print S95
print 1.96*sqrt(totBG+syst**2 * totBG**2) 

# s / sqrt(s+b+syst**2 * b**2) = 1.96
# s95 ~ 1.96*sqrt(b+syst**2 * b**2) 