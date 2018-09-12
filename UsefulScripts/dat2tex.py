"""convert cutflow table to latex, using pandas function"""
import pandas as pd
import sys

if len(sys.argv)!=3:
	print "Incorrect number of arguements"
	print "useage: python dat2tex.py INFILE.dat OUTFILE.tex"
	exit()
df =pd.read_csv(sys.argv[1],sep='\t')
with open(sys.argv[2], 'w') as f:
	f.write(df.to_latex(float_format=lambda x: '%.2f' % x))

