# __author__ = 'WeiFu'
from __future__ import print_function, division
import sys, pdb, random
from ruler import *
from Abcd import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from tuner import *
from processarff import *
from sk import rdivDemo
import weka.core.jvm as jvm
from weka.core.converters import Loader
from weka.classifiers import Classifier
from scipy.integrate import simps,trapz

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
  try:
    ff = open(f, "r")
  except IOError:
    print("Can't open file!")
    return # if we can't open the file, then return None. When processing, we need to take care of None
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
  return XY(predicted)


def C45(train, test):
  return wekaCALL(train, test, "weka.classifiers.trees.J48")


def RIPPER(train, test):
  return wekaCALL(train, test, "weka.classifiers.rules.JRip")


def NaiveBayes(train, test):
  return wekaCALL(train, test, "weka.classifiers.bayes.NaiveBayes")


def wekaCALL(train, test, learner):
  if not jvm.started: jvm.start()
  loader = Loader(classname="weka.core.converters.ArffLoader")
  train_data = loader.load_file(train)
  test_data = loader.load_file(test)
  train_data.class_is_last()
  test_data.class_is_last()
  cls = Classifier(classname=learner)
  cls.build_classifier(train_data)
  predicted, name = [], []
  for index, inst in enumerate(test_data):
    pred = cls.classify_instance(inst)
    if pred != 0:
      predicted += [
        [inst.values[i] for i in range(inst.num_attributes)]]  # this API changes "false" to 0, and "true" to 1
      name += ["0"]  # this is a fake name for each column, which is made to use data() function in readdata.
  ss = data(names=name, data=predicted)
  return XY(ss.data)


def plot(result):
  # color = ['r-','k-','b-','b^','g-','y-','c-','m-']
  # labels = ['WHICH','Tuned_WHICH','manualUp','manualDown','minimum','best','Tuned_CART','CART']
  color = ['r-', 'k-', 'b-', 'g-', 'y-', 'c-','m-']
  labels = ['WHICH', 'manualUp', 'manualDown', 'minimum', 'best', 'CART','C4.5']
  plt.figure(1)
  for j, x in enumerate(result):
    plt.plot(x[0], x[1], color[j], label=labels[j])
  plt.xlabel("Effort(% LOC inspected)")
  plt.ylabel("PD(% probability of detection)")
  plt.title("Effort-vs-PD")
  plt.ylim(0, 100)
  plt.legend(loc='best')
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
  result = [readcpp(f="/Users/WeiFu/Github/WHICH/cppresults.csv")]
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
    if data == None:
      continue # ignore the none.
    areaLst += [area(data)]
  return percentage(areaLst)


def preSK(stats):
  names = ["manualUp", "manualDown", "C4.5","RIPPER","NaiveBayes", "MICRO-20","WHICH-2", "WHICH-4", "WHICH-8"]
  out = []
  for key, value in stats.iteritems():
    ordered = sorted(value)
    ordered.insert(0, names[key])
    out += [ordered]
  return out

def area(result):
  X = result[0]
  Y = result[1]
  if len(X)== 0 or len(Y) == 0: return 0
  if 100 not in X:
    X = np.append(X,[100]) # if this curve does not reach top right, we need to add it
    Y = np.append(Y,Y[-1]) # just repeat last value in Y
  return trapz(Y,X)

def percentage(lst): # lst[0] is the best which is the base.
  val = []
  if lst[0] == 0 or len(lst) == 0: return val # return empty list
  for i in range(1,len(lst)):
    val +=[lst[i]/lst[0]]
  return val

def crossEval(repeats=10, folds=3, src="../DATASET"):
  def deletelog():
    cppresult = "./cppresults.csv"
    if os.path.exists(cppresult):
      os.remove(cppresult)

  def cppWhich(arfftrain, arfftest, options=""):
    cpp = "././which -t " + arfftrain + " -T " + arfftest + " -score effort -alpha 1 -beta 1000 -gamma 0" + options
    os.system(cpp)

  def process(result):
    mypercentage = postCalculation(result)
    if len(mypercentage) == 0: return  # this is the case, where the best is 0
    if first_Time:  # initialize: for each data set, stats contains all the results of methods for that data set.
      for t, each in enumerate(mypercentage):
        stats[t] = stats.get(t, []) + [each]
      combine[j] = [stats]
    else:
      for t, each in enumerate(mypercentage):
        combine[j][0][t] = combine.get(j)[0][t] + [each]

  def learner(csvtest, csvtrain, arfftest, arfftrain):
    result = []  # keep all learners' results for one evaluation
    result += [gbest(csvtest)]
    result += [manual(csvtest, False)]  # up : ascending order
    result += [manual(csvtest, True)]  # down: descending order
    # result += [cart(csvtrain, csvtest, False)]  # default cart
    result += [C45(arfftrain, arfftest)]
    result += [RIPPER(arfftrain, arfftest)]
    result += [NaiveBayes(arfftrain, arfftest)]
    for para in which_settings:
      deletelog()
      cppWhich(arfftrain, arfftest, para)
      result += [readcpp(f="./cppresults.csv")]
    return result

  combine = {}
  first_Time = True
  files_name = ["ar3", "ar4", "ar5", "cm1", "kc1", "kc2", "kc3", "wm1", "pc"]
  which_settings = [" -micro 20 -bins 2", " -bins 2", " -bins 4",
                    " -bins 8"]  # cmd for micro-20, which-2, which-4, which-8
  for k in range(repeats):
    All(src, folds)  # prepare 3 cross-way evaluation data sets
    datasets = [join(src, f) for f in listdir(src) if not isfile(join(src, f)) and ".git" not in f and ".idea" not in f]
    for j in range(len(datasets)):
      stats = {}  # keep all learners' results for a complete 3 cross evaluation for one data set.
      for i in range(folds):
        csvtrain = readcsv(datasets[j] + '/csv/train' + str(i) + '.csv')
        csvtest = readcsv(datasets[j] + '/csv/test' + str(i) + '.csv')
        arfftrain = datasets[j] + '/arff/train' + str(i) + '.arff'
        arfftest = datasets[j] + '/arff/test' + str(i) + '.arff'
        process(learner(csvtest, csvtrain, arfftest, arfftrain))  # calculate percentage and others.
    first_Time = False
  for key, stats in combine.iteritems():  # print results for each data set
    print("*" * 15 + files_name[key] + "*" * 15)
    out = preSK(stats[0])
    rdivDemo(out)
  print("DONE!")


if __name__ == "__main__":
  # run(main())
  crossEval()