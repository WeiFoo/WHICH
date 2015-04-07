#__author__ = 'WeiFu'
from __future__ import print_function, division
import sys,pdb
from ruler import *
from table import *
from Abcd import *
import numpy as np
import matplotlib.pyplot as plt

def csv(f= "./data/ant/ant-1.5copy.csv"):
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

def XY(data):
  '''generate X, Y for plotting'''
  Loc,TP = 0,0
  xx,pd = [],[]
  for d in data:
    TP += d.cells[-1]
    Loc += d.cells[10]
    xx +=[100*Loc/the.effortNorm.Total[10]]
    pd +=[100*TP/the.NP.defective]
  x = np.array(xx)
  pd = np.array(pd)
  return[x,pd]

def manual(t, up = True):
  data = t.data
  if not up:
    data = sorted(t.data,key = lambda z :z[10], reverse = True)
  return XY(data)

def gbest(t):
  '''the best method which has highest score'''
  data =[d for d in t.data if d[-1] ==1]
  data = sorted(data, key = lambda z: z[10])
  return XY(data)



def plot(result):
  color = ['r-','b-','k-','g-','y-']
  labels = ['manualUp','manualDown','minimum','good','best']
  plt.figure(1)
  # plt.figure(figsize=(8,4))
  for j,x in enumerate(result):
    plt.plot(x[0],x[1],color[j],label =labels[j])
  plt.xlabel("Effort(% LOC inspected)")
  plt.ylabel("PD(% probability of detection)")
  plt.title("Effort-vs-PD")
  plt.ylim(0,100)
  plt.legend(loc='down right')
  # plt.text(60,20,'manualDown')
  # plt.text(35,70,'manualUp')
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
    # actual,predict = best.predict(csv())
    # _Abcd(predict, actual)
    t = csv(f= "./data/ant/ant-1.4copy.csv")
    result=[manual(t)]
    result +=[manual(t,up = False)]
    result +=[[np.linspace(0,100,100),np.linspace(0,100,100)]]
    result +=[best.predict(t)]
    result +=[gbest(t)]
    plot(result)
    # pdb.set_trace()
  run(_ruler)

if __name__ == "__main__":
  _rule()