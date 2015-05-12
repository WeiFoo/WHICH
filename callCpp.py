#__author__ = 'WeiFu'
from __future__ import division
import sys, pdb,os
import numpy as np
from scipy.integrate import simps,trapz


def area(result):
  X = result[0]
  Y = result[1]
  # X = np.array([0,50,100])
  # Y = np.array([0,50,0])
  if len(X)== 0 or len(Y) == 0: return 0
  if 100 not in X:
    X = np.append(X,[100]) # if this curve does not reach top right, we need to add it
    Y = np.append(Y,Y[-1]) # just repeat last value in Y
  return trapz(Y,X)

def percentage(lst): # lst[0] is the best which is the base.
  val = []
  if lst[0] == 0 or len(lst) == 0: raise ValueError("The Best dose not exist!")
  for i in range(1,len(lst)):
    val +=[lst[i]/lst[0]]
  return val






def call():
  # os.system("./CppVersion1.0/cpp/make")
  os.system("/Users/WeiFu/Github/WHICH/CppVersion1.0/cpp/./which -t /Users/WeiFu/Github/WHICH/CppVersion1.0/cpp/cm1Train.arff -T /Users/WeiFu/Github/WHICH/CppVersion1.0/cpp/cm1Test.arff -score effort")

if __name__ == "__main__":
  print(area(None))
