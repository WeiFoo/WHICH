#__author__ = 'WeiFu'
from __future__ import print_function, division
import sys,pdb,csv,random
from ruler import *
from Abcd import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from tuner import *
from processarff import *
from callCpp import *
from sk import rdivDemo


@setting
def cart(**d):
  return o(
        max_features = None,
        max_depth = None,
        min_samples_split = 2,
        min_samples_leaf = 1
  ).update(**d)

def readcsv(f= "./data/ant/ant-1.7copy.csv"):
  ff = open(f,"r")
  # content = ff.readline().split("\r")
  content = ff.readlines()
  n = content[0].split(",")
  d =[ map(float,row.split(",")) for row in content[1:]]
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
    Loc += d.cells[the.DATA.loc]
    xx +=[100*Loc/the.DATA.total[the.DATA.loc]]
    pd +=[100*TP/the.DATA.defective]
  x = np.array(xx)
  pd = np.array(pd)
  return[x,pd]

def manual(t, up = False):
  # data = t.data
  data = sorted(t.data,key = lambda z :z[the.DATA.loc], reverse = up)
  return XY(data)

def gbest(t):
  '''the best method which has highest score'''
  data =[d for d in t.data if d[-1] ==1]
  data = sorted(data, key = lambda z: z[the.DATA.loc])
  return XY(data)
def readcpp(f):
  ff = open(f,"r")
  # pdb.set_trace()
  X = map(float,ff.readline().split(",")[:-1]) # this line is X
  Pd = map(float,ff.readline().split(",")[:-1]) # this line is Pd
  return[np.array(X), np.array(Pd)]

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
  predicted_sorted = sorted(predicted, key = lambda z:z.cells[the.DATA.loc])
  for p in predicted_sorted:
    if p.cells[-1] == 1:
      TP += 1
    Loc += p.cells[the.DATA.loc]
    x +=[100*Loc/the.DATA.total[the.DATA.loc]]
    pd +=[100*TP/the.DATA.defective]
  x = np.array(x)
  pd = np.array(pd)
  return[x,pd]


def plot(result):

  # color = ['r-','k-','b-','b^','g-','y-','c-','m-']
  # labels = ['WHICH','Tuned_WHICH','manualUp','manualDown','minimum','best','Tuned_CART','CART']
  color = ['r-','k-','b-','g-','y-','c-']
  labels = ['WHICH','manualUp','manualDown','minimum','best','CART']
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

def _rule(train):
  LIB(seed=1)
  #RULER(tiny=4,better=gt) initialize
  # print(train.score, "baseline :",len(train.data))
  for z in ruler(train):
    print(z.score,z)
  try:
    best = ruler(train)[0]
  except IndexError, e:
    return None
  return best

def which():
  train=readcsv(f= "./data/ant/ant-1.7copy.csv")
  test = readcsv(f= "./data/ant/ant-1.7copy.csv")
  bestrule = _rule(train)
  if bestrule:
    result =[bestrule.predict(test)]
    if not Settings.tunner.isTuning:
      return result # not tuning
    else:
      # return result[0][1][-1]/(result[0][0][-1]+0.00001) if len(result[0][0]) != 0 else 0
      return result[0][1][-1] if len(result[0][0]) != 0 else 0
        # this is tuning score, the last point in curve: pd/effort
  else:
      return 0 # no rules, then return 0

def main():
  train= readcsv(f= "/Users/WeiFu/Github/DATASET/newcsv/CM1train.csv")
  test = readcsv(f= "/Users/WeiFu/Github/DATASET/newcsv/CM1test.csv")
  # train= readcsv(f= "./data/cm1/cm1Train.arff.csv")
  # test = readcsv(f= "./data/cm1/cm1Test.arff.csv")
  # ============python which============
  bestrule = _rule(train)
  result =[bestrule.predict(test)]
  result =[readcpp(f="/Users/WeiFu/Github/WHICH/CppVersion1.0/cpp/Rule111.csv")]
  # ============tuned WHICH and CART============
  # TUNER = Which()
  # TUNER.DE()
  # result +=which()
  # TUNER = Cart()
  # TUNER.DE()

  result += [manual(test, False)] # up : ascending order
  result += [manual(test,True)] # down: descending order
  result += [[np.linspace(0,100,100),np.linspace(0,100,100)]]
  result += [gbest(test)]
  # result += [cart(train,test)] # tuned cart
  result += [cart(train,test,False)] # default cart
  # pdb.set_trace()
  plot(result)

def postCalculation(result):
  areaLst = []
  for data in result:
    areaLst += [area(data)]
  return percentage(areaLst)
def preSK(stats):
  names = ["manualUp","manualDown","CART","WHICH-2"]
  out = []
  for key,value in stats.iteritems():
    ordered = sorted(value)
    ordered.insert(0,names[key])
    out +=[ordered]
    pdb.set_trace()
  return out




def crossEval(repeats = 10, folds = 3,src = "/Users/WeiFu/Github/DATASET"):
  cppresult = "/Users/WeiFu/Github/WHICH/CppVersion1.0/cpp/Rule111.csv"
  stats = {}
  for k in range(3):
    All(src,folds)
    folders = [ join(src,f) for f in listdir(src) if not isfile(join(src,f)) and ".git" not in f and ".idea" not in f]
    for j in range(1):
      for i in range(folds):
        result = []
        if os.path.exists(cppresult):
          os.remove(cppresult)
        csvtrain = readcsv(folders[j]+'/csv/train'+str(i)+'.csv')
        csvtest = readcsv(folders[j]+'/csv/test'+str(i)+'.csv')
        arfftrain = folders[j]+'/arff/train'+str(i)+'.arff'
        arfftest = folders[j]+'/arff/test'+str(i)+'.arff'
        cpp = "/Users/WeiFu/Github/WHICH/CppVersion1.0/cpp/./which -t "+arfftrain+" -T "+ arfftest+" -score effort -bins 2"
        os.system(cpp)
        result +=[gbest(csvtest)]
        result += [manual(csvtest, False)] # up : ascending order
        result += [manual(csvtest,True)] # down: descending order
        result += [cart(csvtrain,csvtest,False)] # default cart
        result += [readcpp(f="/Users/WeiFu/Github/WHICH/CppVersion1.0/cpp/Rule111.csv")]
        mypercentage = postCalculation(result)
        for t, each in enumerate(mypercentage):
          stats[t] = stats.get(t,[])+[each]
  out = preSK(stats)
  pdb.set_trace()
  rdivDemo(out)
  print("DONE!")



if __name__ == "__main__":
  # run(main())
  crossEval()