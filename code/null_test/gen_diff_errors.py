from numpy import *
##TODO need a script here that takes all the measured reference beam
##data, projects it onto a healpix (can pull methods out of divide_out_sats.py
##to get the same rotations). Then compare it to the rotated ung reference models,
##and fit the differences, like is done in Figure 4 of the paper
##then take slices through the difference to make an numpy save file of this
##format

length = 56

##Each of these is a slice through the healpix projection of the difference between
##the measured refernce beam map and the model, for both rf0 and rf1
ew_rf0 = ones(length)
ew_rf1 = ones(length)
ns_rf0 = ones(length)
ns_rf1 = ones(length)

savez_compressed('model_difference.npz',ew_rf0=ew_rf0,ew_rf1=ew_rf1,ns_rf0=ns_rf0,ns_rf1=ns_rf1)
