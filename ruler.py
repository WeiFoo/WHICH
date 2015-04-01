from __future__ import division,print_function
import sys,random,pdb
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
             beta = 1000,
             gamma = 0,
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

  def computeB(i):
    FP, TP,Loc = 0,0,0,
    for row in i.rows:
      Loc += row[10] # this is loc, # 10
      if row[-1]==0:
        FP += 1
      else:
        TP += 1
    pd = TP/the.NP.defective
    pf = FP/the.NP.nondefective
    print(str(pf))
    effort = Loc/the.effortNorm.Total[10]# this is normalized effort
    alpha = the.RULER.rules.alpha
    beta = the.RULER.rules.beta
    gamma = the.RULER.rules.gamma
    B = (pd**2*alpha +(1-pf)**2*beta\
        +(1-effort)**2*gamma)**0.5/(alpha+beta+gamma)**0.5
    return B
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
  # pdb.set_trace()
  for column  in t.indep:
    tmp = sdiv(t.data,attr=t.names[column],
              tiny = the.RULER.rules.tiny,
              x    = lambda z : z[column],
              y    = lambda z : z.score,
              small= the.RULER.rules.small)
    if len(tmp) > 1: # this column is useful
        out += tmp
  return [one for one in out if # better mu than b4
          better(one.y.mu,atLeast)]

def ruler(t):
  retries = xrange(the.RULER.rules.retries)
  repeats = xrange(the.RULER.rules.repeats)
  out     = []
  taboo   = set() #??????
  ranges0 = ranges(t)
  pdb.set_trace()
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
                pdb.set_trace()
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
