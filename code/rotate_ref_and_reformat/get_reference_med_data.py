from numpy import *
import healpy as hp
import matplotlib.pyplot as plt
from astropy.stats import median_absolute_deviation

print('doing rf0')
##Grab reference data for rf0, and get the median and median absolute deviation of the data
##Save in a compressed file
data_rf0 = load('../divide_out_sats/rotated_sat-removed_full_AUT_S21XX_ref_rf0XX.npz',allow_pickle=True)
raw_dB_rf0 = data_rf0['ref_tile_map_dB_med']
med_dB_rf0 = [median(pixel) for pixel in raw_dB_rf0]
mad_dB_rf0 = [median_absolute_deviation(pixel) for pixel in raw_dB_rf0]
savez_compressed('rotated_med_dB_rf0',med_dB_rf0=med_dB_rf0,mad_dB_rf0=mad_dB_rf0)

print('doing rf1')
##Do it again for rf1
data_rf1 = load('../divide_out_sats/rotated_sat-removed_full_AUT_S21XX_ref_rf1XX.npz',allow_pickle=True)
raw_dB_rf1 = data_rf1['ref_tile_map_dB_med']
med_dB_rf1 = [median(pixel) for pixel in raw_dB_rf1]
mad_dB_rf1 = [median_absolute_deviation(pixel) for pixel in raw_dB_rf1]
savez_compressed('rotated_med_dB_rf1',med_dB_rf1=med_dB_rf1,mad_dB_rf1=mad_dB_rf1)
