# __author__ = 'WeiFu'
from __future__ import print_function, division
import sys, pdb, csv, random
from ruler import *
from Abcd import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from tuner import *
from processarff import *
from callCpp import *
from sk import rdivDemo
import weka.core.jvm as jvm
from weka.core.converters import Loader
from weka.classifiers import Classifier


@setting
def cart(**d):
  """
  this is for tuning cart.
  """
  return o(
    max_features=None,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1
  ).update(**d)


def readcsv(f="./data/ant/ant-1.7copy.csv"):
  ff = open(f, "r")
  # content = ff.readline().split("\r")
  content = ff.readlines()
  n = content[0].split(",")
  d = [map(float, row.split(",")) for kk, row in enumerate(content[1:])]
  return data(names=n, data=d)


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


def XY(mydata, flag = False):
  '''generate X, Y coordinates for plotting'''
  data = sorted(mydata, key=lambda z: z[the.DATA.loc], reverse = flag )
  Loc, TP = 0, 0
  xx, pd = [], []
  for d in data:
    if d.cells[-1] == 1:
      TP += d.cells[-1]
    Loc += d.cells[the.DATA.loc]
    xx += [100 * Loc / the.DATA.total[the.DATA.loc]]
    pd += [100 * TP / (the.DATA.defective + 0.00001)]
  x = np.array(xx)
  pd = np.array(pd)
  return [x, pd]


def manual(t, up=False):
  """
  false : ascending order ==> UP method
  true : descending order ==> Down method
  """
  # data = sorted(t.data, key=lambda z: z[the.DATA.loc], reverse=up)
  return XY(t.data, up)


def gbest(t):
  '''the best method which has highest score'''
  mydata = [d for d in t.data if d[-1] == 1]
  # data = sorted(data, key=lambda z: z[the.DATA.loc])
  return XY(mydata)


def readcpp(f):
  ff = open(f, "r")
  X = map(float, ff.readline().split(",")[:-1])  # this line is X
  Pd = map(float, ff.readline().split(",")[:-1])  # this line is Pd
  return [np.array(X), np.array(Pd)]


def sklearn_data(train, test):
  train_x = [t.cells[:-1] for t in train.data]
  train_y = [(t.cells[-1]) for t in train.data]
  test_x = [t.cells[:-1] for t in test.data]
  test_y = [(t.cells[-1]) for t in test.data]
  return [train_x, train_y, test_x, test_y]


def cart(train, test, tuning=True):
  data = sklearn_data(train, test)
  clf = DecisionTreeRegressor(random_state=1, max_features=the.cart.max_features, max_depth=the.cart.max_depth,
                              min_samples_split=the.cart.min_samples_split,
                              min_samples_leaf=the.cart.min_samples_leaf).fit(data[0], data[1])
  if not tuning:  # default cart
    clf = DecisionTreeRegressor(random_state=1).fit(data[0], data[1])
  predictresult = [i for i in clf.predict(data[2])]  # to change the format from ndarray to list
  predicted = [test.data[j] for j, p in enumerate(predictresult) if
               p == 1]  # all these data are predicted to be defective
  # predicted_sorted = sorted(predicted, key=lambda z: z.cells[the.DATA.loc])
  # pdb.set_trace()
  return XY(predicted)

def wekaC45(train, test):
  if not jvm.started:jvm.start()
  loader = Loader(classname="weka.core.converters.ArffLoader")
  train_data = loader.load_file(train)
  test_data = loader.load_file(test)
  train_data.class_is_last()
  test_data.class_is_last()
  cls = Classifier(classname="weka.classifiers.trees.J48", options=["-C", "0.5"])
  cls.build_classifier(train_data)
  predicted, name = [], []
  for index, inst in enumerate(test_data):
    pred = cls.classify_instance(inst)
    if pred != 0:
      predicted += [[inst.values[i]for i in range(inst.num_attributes)]] # this API changes "false" to 0, and "true" to 1
      name +=["0"] # this is a fake name for each column, which is made to use data() function in readdata.
  ss = data(names = name,data =predicted)
  return XY(ss.data)


def plot(result):
  # color = ['r-','k-','b-','b^','g-','y-','c-','m-']
  # labels = ['WHICH','Tuned_WHICH','manualUp','manualDown','minimum','best','Tuned_CART','CART']
  color = ['r-', 'k-', 'b-', 'g-', 'y-', 'c-','m-']
  labels = ['WHICH', 'manualUp', 'manualDown', 'minimum', 'best', 'CART','C4.5']
  plt.figure(1)
  # plt.figure(figsize=(8,4))
  for j, x in enumerate(result):
    plt.plot(x[0], x[1], color[j], label=labels[j])
  plt.xlabel("Effort(% LOC inspected)")
  plt.ylabel("PD(% probability of detection)")
  plt.title("Effort-vs-PD")
  plt.ylim(0, 100)
  plt.legend(loc='best')
  # plt.text(60,20,'manualDown')
  # plt.text(35,70,'manualUp')
  plt.show()


def _rule(train):
  LIB(seed=1)
  #RULER(tiny=4,better=gt) initialize
  # print(train.score, "baseline :",len(train.data))
  for z in ruler(train):
    print(z.score, z)
  try:
    best = ruler(train)[0]
  except IndexError, e:
    return None
  return best


def which():
  train = readcsv(f="./data/ant/ant-1.7copy.csv")
  test = readcsv(f="./data/ant/ant-1.7copy.csv")
  bestrule = _rule(train)
  if bestrule:
    result = [bestrule.predict(test)]
    if not Settings.tunner.isTuning:
      return result  # not tuning
    else:
      # return result[0][1][-1]/(result[0][0][-1]+0.00001) if len(result[0][0]) != 0 else 0
      return result[0][1][-1] if len(result[0][0]) != 0 else 0
      # this is tuning score, the last point in curve: pd/effort
  else:
    return 0  # no rules, then return 0


def main():
  train = readcsv(f="/Users/WeiFu/Github/DATASET/newcsv/CM1train.csv")
  test = readcsv(f="/Users/WeiFu/Github/DATASET/newcsv/CM1test.csv")
  # train= readcsv(f= "./data/cm1/cm1Train.arff.csv")
  # test = readcsv(f= "./data/cm1/cm1Test.arff.csv")
  # ============python which============
  bestrule = _rule(train)
  result = [bestrule.predict(test)]
  result = [readcpp(f="/Users/WeiFu/Github/WHICH/CppVersion1.0/cpp/Rule111.csv")]
  # ============tuned WHICH and CART============
  # TUNER = Which()
  # TUNER.DE()
  # result +=which()
  # TUNER = Cart()
  # TUNER.DE()
  result += [manual(test, False)]  # up : ascending order
  result += [manual(test, True)]  # down: descending order
  result += [[np.linspace(0, 100, 100), np.linspace(0, 100, 100)]]
  result += [gbest(test)]
  # result += [cart(train,test)] # tuned cart
  result += [cart(train, test, False)]  # default cart
  # pdb.set_trace()
  plot(result)


def postCalculation(result):
  areaLst = []
  for data in result:
    areaLst += [area(data)]
  return percentage(areaLst)


def preSK(stats):
  names = ["manualUp", "manualDown", "CART","C4.5", "WHICH-2", "WHICH-4", "WHICH-8"]
  out = []
  for key, value in stats.iteritems():
    ordered = sorted(value)
    ordered.insert(0, names[key])
    out += [ordered]
  return out


def crossEval(repeats=10, folds=3, src="../DATASET"):
  def deletelog():
    cppresult = "./CppVersion1.0/cpp/Rule111.csv"
    if os.path.exists(cppresult):
      os.remove(cppresult)

  def cppWhich(arfftrain, arfftest, bin):
    cpp = "./CppVersion1.0/cpp/./which -t " + arfftrain + " -T " + arfftest + " -score effort -bins " + bin
    os.system(cpp)

  combine = {}
  files_name = ["ar3", "ar4", "ar5", "cm1", "kc1", "kc2", "kc3", "wm1", "pc"]
  first_Time = True
  for k in range(1):
    All(src, folds)
    folders = [join(src, f) for f in listdir(src) if not isfile(join(src, f)) and ".git" not in f and ".idea" not in f]
    for j in range(len(folders)):
      stats = {}
      for i in range(1):
        print(folders[j])
        result = []
        deletelog()
        csvtrain = readcsv(folders[j] + '/csv/train' + str(i) + '.csv')
        csvtest = readcsv(folders[j] + '/csv/test' + str(i) + '.csv')
        arfftrain = folders[j] + '/arff/train' + str(i) + '.arff'
        arfftest = folders[j] + '/arff/test' + str(i) + '.arff'
        cppWhich(arfftrain, arfftest, "2")
        result += [gbest(csvtest)]
        result += [manual(csvtest, False)]  # up : ascending order
        result += [manual(csvtest, True)]  # down: descending order
        result += [cart(csvtrain, csvtest, False)]  # default cart
        result += [wekaC45(arfftrain,arfftest)]
        result += [readcpp(f="./CppVersion1.0/cpp/Rule111.csv")]
        deletelog()
        cppWhich(arfftrain, arfftest, "4")
        result += [readcpp(f="./CppVersion1.0/cpp/Rule111.csv")]
        deletelog()
        cppWhich(arfftrain, arfftest, "8")
        result += [readcpp(f="./CppVersion1.0/cpp/Rule111.csv")]
        mypercentage = postCalculation(result)
        if len(mypercentage) == 0: continue  #this is the case, where the best is 0
        if first_Time:
          for t, each in enumerate(mypercentage):
            stats[t] = stats.get(t, []) + [each]
          combine[j] = [stats]
        else:
          for t, each in enumerate(mypercentage):
            combine[j][0][t] = combine.get(j)[0][t] + [each]
    first_Time = False
  for key, stats in combine.iteritems():  # print results for each data set
    print("*" * 15 + files_name[key] + "*" * 15)
    out = preSK(stats[0])
    rdivDemo(out)
  print("DONE!")


if __name__ == "__main__":
  # run(main())
  crossEval()