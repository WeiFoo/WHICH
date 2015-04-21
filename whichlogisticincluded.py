#__author__ = 'WeiFu'
from __future__ import print_function, division
import sys,pdb
from ruler import *
from table import *
from Abcd import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn import linear_model

def csv(f= "./data/ant/ant-1.7copy.csv"):
  t = table(f)
  n = [ header.name for header in t.headers]
  d = sorted([ row.cells for row in t._rows],key =lambda z: z[10] ) # sorted by $loc
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
    xx +=[100*Loc/the.DATA.total[10]]
    pd +=[100*TP/the.DATA.defective]
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
  predicted = []
  for j,p in enumerate(predictresult):
    if p == 1:
      predicted.append(test.data[j])
  predicted_sorted = sorted(predicted, key = lambda z:z.cells[10])
  for p in predicted_sorted:
    if p.cells[-1] == 1:
      TP += 1
    Loc += p.cells[10]
    x +=[100*Loc/the.DATA.total[10]]
    pd +=[100*TP/the.DATA.defective]
  x = np.array(x)
  pd = np.array(pd)
  return[x,pd]

def logistic(train,test):
  TP,Loc = 0,0
  x,pd = [],[]
  train_x =[ t.cells[:-1]for t in train.data]
  train_y = [(t.cells[-1]) for t in train.data]
  test_x = [t.cells[:-1] for t in test.data]
  test_y = [(t.cells[-1]) for t in test.data]
  clf = linear_model.LogisticRegression()
  clf = clf.fit(train_x,train_y)
  array = clf.predict(test_x)
  predictresult = [i for i in array]
  predicted = []
  for j,p in enumerate(predictresult):
    if p == 1:
      predicted.append(test.data[j])
  predicted_sorted = sorted(predicted, key = lambda z:z.cells[10])
  for p in predicted_sorted:
    if p.cells[-1] == 1:
      TP += 1
    Loc += p.cells[10]
    x +=[100*Loc/the.DATA.total[10]]
    pd +=[100*TP/the.DATA.defective]
  x = np.array(x)
  pd = np.array(pd)
  return[x,pd]




def plot(result,trainname,testname):
  color = ['r-','b-','k-','g^','y-','c-','r^']
  labels = ['manualUp','manualDown','minimum','WHICH','best','CART','Logistic']
  plt.figure(1)
  # plt.figure(figsize=(8,4))
  for j,x in enumerate(result):
    plt.plot(x[0],x[1],color[j],label =labels[j])
  plt.xlabel("Effort(% LOC inspected)")
  plt.ylabel("PD(% probability of detection)")
  plt.title(trainname+" "+testname)
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
  f = "./data/ant/ant-1.4copy.csv"
  train=csv(f)
  trainname = "train:"+f[-15:-8]
  bestrule=_rule(train)
  f= "./data/ant/ant-1.7copy.csv"
  testname = "test:"+f[-15:-8]
  test = csv(f)
  result=[manual(test)]
  result +=[manual(test,up = False)]
  result +=[[np.linspace(0,100,100),np.linspace(0,100,100)]]
  result +=[bestrule.predict(test)]
  result +=[gbest(test)]
  result +=[cart(train,test)]
  result +=[logistic(train,test)]
  # pdb.set_trace()
  plot(result, trainname, testname)


if __name__ == "__main__":
  run(_main())