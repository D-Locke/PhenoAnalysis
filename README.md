# PhenoAnalysis
This is a python HEP data analysis framework, with minimalist LHE & ROOT file readers that will iterate over file and store requested observables
in dataframe. Uses DELPHES output tree descriptions. Currently will streamline cut and count analysis, and eventially have some automatic analysis prototyping features.

## Requirements:
ROOT, pyROOT, libDelphes, pandas, numpy, matplotlib

## Features:
* input .lhe or .root from Delphes
* define observables using ROOTs TLorentzvector methods
* compute observables and store in pandas dataframe
* apply user supplied cut-flow
* plot histograms and 2D dalitz plots for all observable combinations
* Will store computed dataframes to improve speed next time doing cuts/plots

### Added:
* combined ROOT and LHE codes, made shared modules
* add better logic for signal specific backgrounds
* parallelize object initialization

### Future:
* improve speed by using iterators
* cProfile code to find slow parts of ROOT code
* check stored dataframe contains all requested observables - ifnot then compute extra columns and append
* add errors - statistical and from cuts (binomial)
* simple multivariate analysis
* Improve storage of dataframes alongside metadata (in hdf5)
* add support for hdf5 and compressing files, which stores ROOTdata metadata along with dataframe
* Add decision trees, neural networks with scikit-learn?
