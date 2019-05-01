# -*- coding: utf-8 -*-

# Download data from: https://neo.sci.gsfc.nasa.gov/view.php?datasetId=MOD_NDVI_M

import argparse
import gzip
import numpy as np
import numpy.ma as ma
from PIL import Image
from pprint import pprint
import sys

from lib.io_utils import *
from lib.math_utils import *

# input
parser = argparse.ArgumentParser()
parser.add_argument('-before', dest="FILE_BEFORE", default="data/MOD_NDVI_M_2000-06-01_rgb_3600x1800.CSV.gz", help="Csv file of data before")
parser.add_argument('-after', dest="FILE_AFTER", default="data/MOD_NDVI_M_2018-06-01_rgb_3600x1800.CSV.gz", help="Csv file of data after")
parser.add_argument('-grad', dest="COLOR_GRADIENT", default="#CE2929,#1D9831", help="Comma separated color gradient")
parser.add_argument('-range', dest="DATA_RANGE", default="-0.3,0.3", help="Expected data range of delta. Execute with -probe to get a sense of what this should be")
parser.add_argument('-dc', dest="DEFAULT_COLOR", default="#000000", help="Default color")
parser.add_argument('-fill', dest="FILL_VALUE", default=99999.0, type=float, help="Fill value")
parser.add_argument('-out', dest="OUTPUT_FILE", default="output/mod_ndvi_200006-201806.png", help="Output file")
parser.add_argument('-probe', dest="PROBE", action="store_true", help="Just spit out debug info?")
a = parser.parse_args()

if "," in a.COLOR_GRADIENT:
    COLOR_GRADIENT = [hex2rgb(c) for c in a.COLOR_GRADIENT.strip().split(",")]
else:
    COLOR_GRADIENT = getColorGradient(a.COLOR_GRADIENT)
DATA_RANGE = tuple([float(d) for d in a.DATA_RANGE.strip().split(",")])
DEFAULT_COLOR = hex2rgb(a.DEFAULT_COLOR)

valuesBefore = readCsv(a.FILE_BEFORE, a.FILL_VALUE)
valuesAfter = readCsv(a.FILE_AFTER, a.FILL_VALUE)

print("Before data shape: %s, %s" % valuesBefore.shape)
print("After data shape: %s, %s" % valuesAfter.shape)

print("Before data range: %s, %s" % (valuesBefore.min(), valuesBefore.max()))
print("After data range: %s, %s" % (valuesAfter.min(), valuesAfter.max()))

# dataMin = min(valuesBefore.min(), valuesAfter.min())
# dataMax = min(valuesBefore.max(), valuesAfter.max())
# dataRange = (dataMin, dataMax)

deltaValues = valuesAfter - valuesBefore
print("Delta data range: %s, %s" % (deltaValues.min(), deltaValues.max()))

# If probing, show a histogram of the data and exit
if a.PROBE:
    from matplotlib import pyplot as plt
    plt.figure(figsize=(16,8))
    # ax = plt.subplot(2, 1, 1)
    # ax.set_title("Data before")
    # plt.hist(valuesBefore.reshape(-1), bins=100)
    # ax = plt.subplot(2, 1, 2)
    # ax.set_title("Data after")
    # plt.hist(valuesAfter.reshape(-1), bins=100)
    plt.hist(deltaValues.reshape(-1), bins=100)
    plt.tight_layout()
    plt.show()
    sys.exit()

dataH, dataW = deltaValues.shape
pixelData = np.zeros((dataH, dataW, 4), dtype=np.uint8)

total = dataH * dataW
print("Converting data to colors...")
for i in range(dataH):
    for j in range(dataW):
        delta = deltaValues[i, j]
        color = [0,0,0,0]
        if not ma.is_masked(delta):
            nvalue = norm(delta, DATA_RANGE, limit=True)
            color = getColor(COLOR_GRADIENT, nvalue)
        pixelData[i, j] = np.array(color, dtype=np.uint8)
        printProgress(i*dataW+j, total)

print("Writing data to image...")
dataIm = Image.fromarray(pixelData, mode="RGBA")
baseIm = Image.new(mode="RGBA", size=(dataW, dataH), color=(0, 0, 0, 255))
baseIm = Image.alpha_composite(baseIm, dataIm)
baseIm = baseIm.convert("RGB")
baseIm.save(a.OUTPUT_FILE)
print("Saved %s" % a.OUTPUT_FILE)
