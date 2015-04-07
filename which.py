#__author__ = 'WeiFu'
from __future__ import print_function, division
import sys,pdb,random
from ruler import *
from table import *
from Abcd import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.cross_validation import KFold

def csv(f= "./data/ant/ant-1.7copy.csv"):
  t = table(f)
  names = [ header.name for header in t.headers]
  rows = [ row.cells for row in t._rows]
  return names,rows
  # d = sorted(,key =lambda z: z[10] ) # sorted by $loc
  # pdb.set_trace()
  # return data(names= n, data = d)
  # return n,d

def threeCV(n,rows, N = 3):
  length = len(rows)
  fold_size = length//N *np.ones(N)
  fold_size[:length%N] +=1
  last = 0
  for i in fold_size:
    yield rows[last:last+i]
  # kf = KFold(temp, n_folds=3,shuffle=True)
  # for train,test in kf:
  #   train_sorted = sorted([rows[i] for i in train],key= lambda z:z[10])
  #   test_sorted = sorted([rows[i] for i in test],key= lambda z:z[10])
  #   yield data(names = n, data = train_sorted),data(names = n, data = test_sorted)

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

def cart(train,test):
  TP,Loc = 0,0
  x,pd = [],[]
  train_x =[ t.cells[:-1]for t in train.data]
  train_y = [(t.cells[-1]) for t in train.data]
  test_x = [t.cells[:-1] for t in test.data]
  test_y = [(t.cells[-1]) for t in test.data]
  clf = DecisionTreeRegressor(random_state = 1).fit(train_x,train_y)
  array = clf.predict(test_x)
  predictresult = [i for i in array]
  for i,d in enumerate(test.data):
    if d.cells[-1] == predictresult[i] and predictresult[i] ==1:
      TP+=1
    Loc += d.cells[10]
    x +=[100*Loc/the.effortNorm.Total[10]]
    pd +=[100*TP/the.NP.defective]
  x = np.array(x)
  pd = np.array(pd)
  # pdb.set_trace()
  return[x,pd]



def plot(result):
  color = ['r-','b-','k-','g-','y-','c-']
  labels = ['manualUp','manualDown','minimum','good','best','CART']
  plt.figure(1)
  # plt.figure(figsize=(8,4))
  for j,x in enumerate(result):
    plt.plot(x[0],x[1],color[j],label =labels[j])
  plt.xlabel("Effort(% LOC inspected)")
  plt.ylabel("PD(% probability of detection)")
  plt.title("Effort-vs-PD")
  plt.ylim(0,100)
  plt.legend(loc='best')
  # plt.text(60,20,'manualDown')
  # plt.text(35,70,'manualUp')
  plt.show()
  pdb.set_trace()

def _rule(train):
  LIB(seed=1)
  RULER(tiny=4,better=gt)
  print(train.score, "baseline :",len(train.data))
  for z in ruler(train):
    print(z.score,z)
  best = ruler(train)[0]
  # actual,predict = best.predict(csv())
  # _Abcd(predict, actual)
  return best

def _main():
  result = []
  N = 3
  for _ in range(10):
    name,rows = csv()
    length = len(rows)
    fold_size = length//N *np.ones(N)
    fold_size[:length%N] +=1
    last = 0
    for i in fold_size:
      start,stop = last, int(last+i)
      test0 = rows[start:stop]
      train0 = rows[:start] +rows[stop:]
      train_sorted = sorted(train0,key= lambda z:z[10])
      test_sorted = sorted(test0,key= lambda z:z[10])
      train = data(names = name, data = train_sorted)
      test = data(names = name, data = test_sorted)
      bestrule=_rule(train)
      # test = csv(f= "./data/ant/ant-1.4copy.csv")
      result +=[manual(test)]
      result +=[manual(test,up = False)]
      result +=[[np.linspace(0,100,100),np.linspace(0,100,100)]]
      result +=[bestrule.predict(test)]
      result +=[gbest(test)]
      result +=[cart(train,test)]
  plot(result)

if __name__ == "__main__":
  run(_main())