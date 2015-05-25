from __future__ import division
import sys
import random
import math
import datetime
import time
import re
import pdb

sys.dont_write_bytecode = True


class Options:

  def __init__(i, **d):
    i.__dict__.update(d)

Settings = Options(de = Options( np = 10,
                              repeats = 1000,
                              f = 0.75,
                              cr = 0.3,
                              bool_index = [],
                              cartLimit_Max = [1, 50, 20, 20, 1],
                              cartLimit_Min = [0.01, 1, 2, 1, 0.01],
                              cart_int_index = [1,2,3],
                              life = 5
                              ),
                   cppwhich = Options(
                              limit = [20,1,1,1,1], #bins, improvement, alpha, beta, gamma
                              which_int_index = [0],
                              which_float_index = [1,2,3,4],
                              ),
                   tunner = Options(isTuning = False),
                   src = Options( train = [],
                                  tune = [],
                                  test = [],
                         )
                   )