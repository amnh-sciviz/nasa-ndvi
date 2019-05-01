# -*- coding: utf-8 -*-

import csv
import gzip
import numpy as np
import numpy.ma as ma
import os
from pprint import pprint
import sys

def printProgress(step, total):
    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*step/total*100,2))
    sys.stdout.flush()


def readCsv(filename, fillValue=None):
    values = np.array([])
    if os.path.isfile(filename):
        print("Reading %s..." % filename)
        lines = []
        f = gzip.open(filename, 'rt', encoding="utf8") if filename.endswith(".gz") else open(filename, 'r', encoding="utf8")
        lines = list(f)
        f.close()
        height = len(lines)
        if height > 0:
            width = len(lines[0].split(","))
            values = np.zeros((height, width))
            for i, line in enumerate(lines):
                row = np.zeros(width)
                for j, value in enumerate(line.split(",")):
                    row[j] = float(value)
                values[i] = row

            # mask values that are invalid
            if fillValue is not None:
                values = ma.masked_values(values, fillValue)

    return values
