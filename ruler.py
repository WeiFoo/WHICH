from __future__ import division,print_function
import sys,random,pdb,math
import numpy as np
sys.dont_write_bytecode = True

"""

Multi-objective optimization

"""
from readdata import *
from counts import *

@setting
def RULER(**d):
  def enough(ruleRows,allRows):
      return len(ruleRows) >= len(allRows)**0.5
  return o(
    better = gt,
    rules =o(tiny=20,
             small=0.001,
             repeats=32,
             beam=16,
             retries=32,
             fresh=0.33,
             alpha = 1,
             beta = 0,
             gamma = 1,
             enough=enough)
  ).update(**d)
"""

## Rule: a collection of ranges

"""
class Rule:
  def __init__(i,ranges,rows):
    i.ranges = ranges
    i.keys   = set(map(lambda z:z.key, ranges))
    i.rows   = rows
    # i.score  = sum(map(lambda z:z.score,rows))/len(rows)
    i.score = i.computeB()
    # i.score = i.effortPd()
  def __repr__(i):
    return '%s:%s' % (str(map(str,i.ranges)),len(i.rows))
  def same(i,j): ## how does this work?
    if len(i.keys) < len(j.keys):
      return j.same(i)
    else: # is the smaller a subset of the larger
      return j.keys.issubset(i.keys)
  def __add__(i,j):
   if i.same(j):
     return False
   ranges = list(set(i.ranges + j.ranges)) # list uniques
   ranges = sorted(ranges,key=lambda x:x.attr)
   b4  = ranges[0]
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
   return Rule(ranges,rows)
  def predict(i,t = None):
    '''use the rule to predict'''
    lo = lambda z: z.x.lo
    hi = lambda z: z.x.hi
    TP,Loc = 0,0
    x,pd,col = [],[],{}
    def check(row,col):
      count =0
      for key, val in col.iteritems():
        Flag = False
        for _ in range(val):
          if lo(i.ranges[count])<=row[key]<=hi(i.ranges[count]):
            Flag = True
          count +=1
        if not Flag:
          return 0
      return 1   # pass the rule and predict as defectie
    attr = [ r.attr for r in i.ranges]
    for a in attr:
      temp = t.names.index(a)
      col[temp] = col.get(temp,0) +1
    predicted = []
    for d in t.data:
      if check(d,col) ==1 :
        predicted.append(d)
    predicted_sorted = sorted(predicted, key = lambda z:z.cells[10])
    for p in predicted_sorted:
      if p.cells[-1] == 1:
        TP += 1
      Loc += p.cells[10]
      x +=[100*Loc/the.DATA.total[10]]
      pd +=[100*TP/the.DATA.defective]
    x = np.array(x)
    pd = np.array(pd)
    pdb.set_trace()
    return[x,pd]

  def computeB(i):
 #all the rows associated with this rule will be predicted as defective.
 #then calculate pd,pf, efforts.
 #efforts is normalized
    FP, TP,Loc = 0,0,0
    for row in i.rows:
      Loc += row[10] # this is loc, # 10
      if row[-1]==0:
        FP += 1
      else:
        TP += 1
    pd = TP/the.DATA.defective
    pf = FP/the.DATA.nondefective
    effort = Loc/the.DATA.total[10]# percentage effort
    alpha = the.RULER.rules.alpha
    beta = the.RULER.rules.beta
    gamma = the.RULER.rules.gamma
    B = (pd**2*alpha +(1-pf)**2*beta\
        +(1-effort)**2*gamma)**0.5/(alpha+beta+gamma)**0.5
    # pdb.set_trace()
    return B
  def effortPd(i):
    FP, TP,Loc = 0,0,0
    for row in i.rows:
      Loc += row[10] # this is loc, # 10
      if row[-1]==0:
        FP += 1
      else:
        TP += 1
    pd = TP/the.DATA.defective
    return pd/(Loc/the.DATA.total[10])

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
  better  = the.RULER.better
  pdb.set_trace()
  for column  in t.indep:
    tmp = sdiv(t.data,attr=t.names[column],
              tiny = the.RULER.rules.tiny,
              x    = lambda z : z[column],
              y    = lambda z : z.score,
              small= the.RULER.rules.small)
    if len(tmp) > 1: # this column is useful
        out += tmp
  pdb.set_trace()
  return [one for one in out if # better mu than b4
          better(one.y.mu,atLeast)]
def rangesEqual(t, N = 2):
  def one(lst, col, attr, x = lambda z: z[col]):
    out = []
    last = this = 0
    width = (the.DATA.Hi[col] - the.DATA.Lo[col])/N
    for j,row in enumerate(lst):
      if row[col] <= width and j < (len(lst)-1):
        continue
      else:
          this = j if j<(len(lst)-1) and j != 0 else j+1 # get the last row included
          sub = lst[last:this]
          out +=[Range(attr = attr, x = o(lo = x(sub[0]), hi = x(sub[-1])), rows = sub)]
          width +=width
          last = j
    return out
  result = []
  for col in t.indep:
    result +=one(sorted(t.data, key = lambda x:x.cells[col]), col, attr = t.names[col])
  return result

def rangesSelect(t,method = rangesEqual):
  return method(t)

def ruler(t):
  retries = xrange(the.RULER.rules.retries)
  repeats = xrange(the.RULER.rules.repeats)
  out     = []
  taboo   = set() #??????
  ranges0 = rangesSelect(t)
  # ranges0 = ranges(t)
  # pdb.set_trace()
  while True:
    best  = None
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
            if wellSupported(rule.rows,t): # why this?
              if not tabooed(rule.rows,taboo): # why check this?
                best   = rule
                top    = rule.score
                rules += [rule]
    if best:
      taboo = taboo | best.rows
      out  += [best]
    else:
      break
  return out

def wellSupported(rows,t):
  return the.RULER.rules.enough(rows,t.data)

def tabooed(rows,taboo):
  overlap = len(rows & taboo)
  tooMuch = len(rows) * the.RULER.rules.fresh
  return  overlap >= tooMuch

def bestRules(rules):
  return sorted(rules,
                key=lambda z: z.score)[
                  -1*the.RULER.rules.beam:]

def ranges2Rules(ranges):
  return map(lambda z : Rule([z],z.rows),
             ranges)
