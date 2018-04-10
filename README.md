# PhenoAnalysis
This is a minimalist ROOT file reader that will iterate over file and store requested observables
in dataframe. Uses DELPHES output trees.

## Requirements:
ROOT, pyROOT, libDelphes, pandas, numpy, matplotlib

Features:
* Will produce 2D dalitz plots for all observable combinations
* Can easily add arbitrary new observables in ROOTreader.py
* Will store computed dataframes to improve speed next time doing cuts/plots

Added:
* combined ROOT and LHE codes, made shared modules
* add better logic for signal specific backgrounds
* parallelize object initialization

Future:
* improve speed by using iterators
* check stored dataframe contains all requested observables - ifnot then compute extra columns and append
* add errors - statistical and from cuts (binomial)
* Improve storage of dataframes alongside metadata (in hdf5)
* add support for hdf5 and compressing files, which stores ROOTdata metadata along with dataframe
* Add decision trees, neural networks with scikit-learn?
