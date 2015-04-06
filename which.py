#__author__ = 'WeiFu'
from __future__ import print_function, division
import sys,pdb
from ruler import *
from table import *
from Abcd import *
import numpy as np
import matplotlib.pyplot as plt

def csv(f= "./data/ant/ant-1.4copy.csv"):
  t = table(f)
  n = [ header.name for header in t.headers]
  d = sorted([ row.cells for row in t._rows],key =lambda z: z[10] ) # sorted by $loc
  # pdb.set_trace()
  return data(names= n, data = d)

def _range():
  LIB(seed=1)
  RULER(tiny=4)
  def _ranges():
    for z in ranges(csv()): print(z)
  run(_ranges)

def _Abcd(predicted, actual):
  abcd = Abcd(db='Traing', rx='Testing')
  for act, pre in zip(actual, predicted):
    abcd.tell(act, pre)
  abcd.header()
  score = abcd.ask()
def manual(t, up = True):
  TP,TN,FP,FN,pd,xx = 0,0,0,0,[],[]
  data = t.data
  Loc = 0
  if not up:
    data = sorted(t.data,key = lambda z :z[10], reverse = True)
  for d in data:
    TP += d.cells[-1]
    Loc += d.cells[10]
    xx +=[100*Loc/the.effortNorm.Total[10]]
    pd +=[100*TP/the.NP.defective]
  x = np.array(xx)
  pd = np.array(pd)
  return[x,pd]


def plot(result):
  plt.figure(1)
  # plt.figure(figsize=(8,4))
  for x in result:
    plt.plot(x[0],x[1],"b--")
  plt.xlabel("Effort(% LOC inspected)")
  plt.ylabel("PD(% probability of detection)")
  plt.title("Effort-vs-PD")
  plt.ylim(0,100)
  plt.legend()
  plt.text(60,20,'manualDown')
  plt.text(35,70,'manualUp')
  plt.show()
  pdb.set_trace()

def _rule():
  LIB(seed=1)
  RULER(tiny=4,better=gt)
  def _ruler():
    t=csv()
    print(t.score, "baseline :",len(t.data))
    for z in ruler(t):
      print(z.score,z)
    best = ruler(t)[0]
    actual,predict = best.predict(csv())
    _Abcd(predict, actual)
    result=[manual(t)]
    result +=[manual(t,up = False)]
    result +=[[np.linspace(0,100,100),np.linspace(0,100,100)]]
    plot(result)
    # pdb.set_trace()
  run(_ruler)

if __name__ == "__main__":
  _rule()