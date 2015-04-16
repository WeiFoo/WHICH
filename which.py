#__author__ = 'WeiFu'
from __future__ import print_function, division
import sys,pdb
from ruler import *
from table import *
from Abcd import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from tuner import *


@setting
def cart(**d):
  return o(
        max_features = None,
        max_depth = None,
        min_samples_split = 2,
        min_samples_leaf = 1
  ).update(**d)

def csv(f= "./data/ant/ant-1.7copy.csv"):
  t = table(f)
  n = [ header.name for header in t.headers]
  d = sorted([ row.cells for row in t._rows ],key =lambda z: z[10] ) # sorted by $loc
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

def cart(train,test, tuning = True):
  TP,Loc = 0,0
  x,pd = [],[]
  train_x =[ t.cells[:-1]for t in train.data]
  train_y = [(t.cells[-1]) for t in train.data]
  test_x = [t.cells[:-1] for t in test.data]
  test_y = [(t.cells[-1]) for t in test.data]
  clf = DecisionTreeRegressor(random_state = 1, max_features = the.cart.max_features, max_depth = the.cart.max_depth,
        min_samples_split = the.cart.min_samples_split, min_samples_leaf = the.cart.min_samples_leaf ).fit(train_x,train_y)
  if not tuning: # default cart
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


def plot(result):
  color = ['r-','b-','k-','g-','y-','c-','m-']
  labels = ['WHICH','manualUp','manualDown','minimum','best','Tuned_CART','CART']
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
  #RULER(tiny=4,better=gt) initialize
  print(train.score, "baseline :",len(train.data))
  for z in ruler(train):
    print(z.score,z)
  try:
    best = ruler(train)[0]
  except IndexError, e:
    return None
  return best

def which():
  train=csv(f= "./data/ant/ant-1.5copy.csv")
  test = csv(f= "./data/ant/ant-1.7copy.csv")
  bestrule = _rule(train)
  if bestrule:
    result =[bestrule.predict(test)]
    if not Settings.tunner.isTuning:
      return result # not tuning
    else:
      return result[0][1][-1]/(result[0][0][-1]+0.00001) if len(result[0][0]) != 0 else 0
        # this is tuning score, the last point in curve: pd/effort
  else:
      return 0 # no rules, then return 0
def main():
  train=csv(f= "./data/ant/ant-1.5copy.csv")
  test = csv(f= "./data/ant/ant-1.7copy.csv")
  # result = []
  bestrule = _rule(train)
  result =[bestrule.predict(test)]
  # TUNER = Which()
  # TUNER.DE()
  # result =which()
  # pdb.set_trace()
  TUNER = Cart()
  TUNER.DE()
  pdb.set_trace()
  result += [manual(test)]
  result += [manual(test,up = False)]
  result += [[np.linspace(0,100,100),np.linspace(0,100,100)]]
  result += [gbest(test)]
  result += [cart(train,test)] # tuned cart
  result += [cart(train,test,False)] # default cart
  plot(result)


if __name__ == "__main__":
  run(main())