# PhenoAnalysis
This is a python HEP data analysis framework, with minimalist LHE & ROOT file readers that will iterate over file and store requested observables
in dataframe. Uses DELPHES output tree descriptions. Currently will streamline cut and count analysis, and eventially have some automatic analysis prototyping features.

Reading of files is done in parallel, using multiprocessing module.

## Requirements:
Python2.x, ROOT5.x, pyROOT, libDelphes, pandas, numpy, matplotlib

### Installation:
1. Install python modules (pandas,numpy,matplotlib)
...```pip install numpy pandas matplotlib```
2. Install ROOT, as described here: https://root.cern.ch/pyroot
3. Build Delphes 3.x and dir containing libDelphes.so in LD_LIBRARY_PATH (or place in e.g ~Packages/root/build/lib/root/)
4. Make sure root is sourced, and libDelphes.so can be found
...```python -c "import ROOT"```
5. If using ROOT6: In PhenoAnalysis/PhenoAnalysis/ROOTreader.py, lines 10,11 - change path to your Delphes dir

### Adding new analysis:
1. Specify new observables in observables.py, add plot range and labels in plotting.py
2. Write code e.g example1, containing required observables, cuts, and various definitions 


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
* avoid having to edit core code for new processes, observables etc.
* add pdf report generation, with cut-flow tables
* improve speed by using iterators
* instead use upROOT for parsing? Avoids requirement of ROOT install, libDelphes...
* cProfile code to find slow parts of ROOT code
* check stored dataframe contains all requested observables - ifnot then compute extra columns and append
* add errors - statistical and from cuts (binomial)
* simple multivariate analysis
* Improve storage of dataframes alongside metadata (in hdf5)
* add support for hdf5 and compressing files, which stores ROOTdata metadata along with dataframe
* Add decision trees, neural networks with scikit-learn?

## Useful docs
* TLorentzVector: https://root.cern.ch/doc/master/classTLorentzVector.html
* Delphes tree description: https://cp3.irmp.ucl.ac.be/projects/delphes/wiki/WorkBook/RootTreeDescription
