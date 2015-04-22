from __future__ import division, print_function
import sys, random, pdb, math
import numpy as np

sys.dont_write_bytecode = True

"""

Multi-objective optimization

"""
from readdata import *
from counts import *


@setting
def RULER(**d):
  def enough(ruleRows, allRows):
    return len(ruleRows) >= len(allRows) ** the.RULER.rules.enoughPara

  return o(
    better=gt,
    rules=o(tiny=20,
            small=0.001,
            repeats=32,
            retries=32,
            beam=16,
            fresh=0.33,
            enoughPara=0.5,
            alpha=1,
            beta=1000,
            gamma=0,
            enough=enough)
  ).update(**d)


"""

## Rule: a collection of ranges

"""


class Rule:
  def __init__(i, ranges, rows):
    i.ranges = ranges
    i.keys = set(map(lambda z: z.key, ranges))
    i.rows = rows
    # i.score  = sum(map(lambda z:z.score,rows))/len(rows)
    i.score = i.computeB()
    # i.score = i.effortPd()

  def __repr__(i):
    return '%s:%s' % (str(map(str, i.ranges)), len(i.rows))

  def same(i, j):  ## how does this work?
    if len(i.keys) < len(j.keys):
      return j.same(i)
    else:  # is the smaller a subset of the larger
      return j.keys.issubset(i.keys)

  def __add__(i, j):
    if i.same(j):
      return False
    ranges = list(set(i.ranges + j.ranges))  # list uniques
    ranges = sorted(ranges, key=lambda x: x.attr)
    b4 = ranges[0]
    rows = b4.rows
    for now in ranges[1:]:
      # if b4.attr == "$dit" and now.attr == "$mfa":
      # pdb.set_trace()
      if now.attr == b4.attr:
        rows = rows | now.rows
      else:
        rows = rows & now.rows
      if not rows:
        return False
      b4 = now
    return Rule(ranges, rows)

  def predict(i, t=None):
    '''use the rule to predict'''
    x, pd, col = [], [], {}

    def duplicates():
      attr = [r.attr for r in i.ranges]
      for a in attr:
        temp = t.names.index(a)
        col[temp] = col.get(temp, 0) + 1  # count # of same attribute

    def check0():
      duplicates()
      predicted = []
      for d in t.data:
        if check(d, col) == 1:
          predicted.append(d)
      return sorted(predicted, key=lambda z: z.cells[the.DATA.loc])

    def check(row, col, lo=lambda z: z.x.lo, hi=lambda z: z.x.hi):
      count = 0
      for key, val in col.iteritems():
        Flag = False
        for _ in range(val):
          if lo(i.ranges[count]) <= row[key] <= hi(i.ranges[count]):
            Flag = True
          count += 1
        if not Flag:
          return 0
      return 1  # pass the whole rule and predict as defective

    def cal(predicted_sorted):
      TP, Loc = 0, 0
      x, pd = [], []
      for p in predicted_sorted:
        if p.cells[-1] == 1:
          TP += 1
        Loc += p.cells[the.DATA.loc]
        x += [100 * Loc / the.DATA.total[the.DATA.loc]]
        pd += [100 * TP / the.DATA.defective]
      x = np.array(x)
      pd = np.array(pd)
      # pdb.set_trace()
      return [x, pd]

    return cal(check0())


  def computeB(i):
    # all the rows associated with this rule will be predicted as defective.
    #then calculate pd,pf, efforts.
    #efforts is normalized
    FP, TP, Loc = 0, 0, 0
    for row in i.rows:
      Loc += row[the.DATA.loc]
      if row[-1] == 0:
        FP += 1
      else:
        TP += 1
    pd = TP / the.DATA.defective
    pf = FP / (the.DATA.nondefective + 0.00001)
    effort = Loc / the.DATA.total[the.DATA.loc]  # percentage effort
    alpha = the.RULER.rules.alpha
    beta = the.RULER.rules.beta
    gamma = the.RULER.rules.gamma
    B = (pd ** 2 * alpha + (1 - pf) ** 2 * beta \
         + (1 - effort) ** 2 * gamma) ** 0.5 / (alpha + beta + gamma) ** 0.5
    return B

  def effortPd(i):
    FP, TP, Loc = 0, 0, 0
    for row in i.rows:
      Loc += row[the.DATA.loc]
      if row[-1] == 0:
        FP += 1
      else:
        TP += 1
    pd = TP / the.DATA.defective
    return pd / (Loc / the.DATA.total[the.DATA.loc])


"""

Return the ranges:

+ From "useful" columns; i.e. those than can be
  divided into ranges that seperate the performance
  score;
+ Where the mean score of those ranges is better than
  the the mean score of all rows.
  
"""


def ranges(t):
  out = []
  atLeast = t.score
  better = the.RULER.better
  pdb.set_trace()
  for column in t.indep:
    tmp = sdiv(t.data, attr=t.names[column],
               tiny=the.RULER.rules.tiny,
               x=lambda z: z[column],
               y=lambda z: z.score,
               small=the.RULER.rules.small)
    if len(tmp) > 1:  # this column is useful
      out += tmp
  pdb.set_trace()
  return [one for one in out if  # better mu than b4
          better(one.y.mu, atLeast)]


def equal_frequency(t, N=4):
  """
  discretize the continuous variable into equal N bins (equal frequent binning)
  at least, the first N-1 bins are allocated equal # of instances, the last bin
  may contain less
  """
  def one_instance(lst, attr, x=lambda z: z[col]):
    last, dist, out = 0, int(math.ceil(len(lst) / N)), []
    cut = [(j + 1) * dist for j in range(N) if (j + 1) * dist < len(lst)]
    cut.extend([len(lst)])
    for k in cut:
      out.extend([Range(attr=attr, x=o(lo=x(lst[last]), hi=x(lst[k - 1])), rows=lst[last:k])])
      last = k
    return out

  result = []
  for col in t.indep:
    result.extend(one_instance(sorted(t.data, key=lambda x: x[col]), attr=t.names[col]))
  return result


def discretize(t, method='equal_frequency'):
  """
  switch in python
  """
  return {
    'sdiv': ranges,
    'equal_frequency': equal_frequency
  }[method](t)


def ruler(t):
  retries = xrange(the.RULER.rules.retries)
  repeats = xrange(the.RULER.rules.repeats)
  out = []
  taboo = set()  # ??????
  ranges0 = discretize(t)
  while True:
    best = None
    # top   = t.score # issue : here, we should change to 0 or what ever.
    top = 0
    rules = ranges2Rules(ranges0)
    for _ in retries:
      rules = bestRules(rules)
      for _ in repeats:
        rule = ask(rules) + ask(rules)
        # pdb.set_trace()
        if rule:
          if rule.score > top:
            if wellSupported(rule.rows, t):  # # of rows should be greater than threshold
              if not tabooed(rule.rows,
                             taboo):  # the new rule should have less overlap of rows with previous best rules
                best = rule
                top = rule.score
                rules += [rule]
    if best:
      taboo = taboo | best.rows
      out += [best]
    else:
      break
  return out


def wellSupported(rows, t):
  return the.RULER.rules.enough(rows, t.data)


def tabooed(rows, taboo):
  overlap = len(rows & taboo)
  tooMuch = len(rows) * the.RULER.rules.fresh
  return overlap >= tooMuch


def bestRules(rules):
  return sorted(rules,
                key=lambda z: z.score)[
         -1 * the.RULER.rules.beam:]


def ranges2Rules(ranges):
  return map(lambda z: Rule([z], z.rows),
             ranges)
