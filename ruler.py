from __future__ import division,print_function
import sys,random,pdb,math
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
  def predict(i,t = None):
    '''use the rule to predict'''
    lo = lambda z: z.x.lo
    hi = lambda z: z.x.hi
    def check(row,col):
      for j, cell in enumerate(col):
        if row[cell]<lo(i.ranges[j]) or row[cell]>hi(i.ranges[j]):
          return 0
        else:
          continue
      return 1 # pass the rule and predict as defectibe
    attr = [ r.attr for r in i.ranges]
    col = [ t.names.index(a) for a in attr]
    defective,actual = [],[]
    for d in t.data:
      actual +=[d.cells[-1]]
      defective += [check(d,col)]
    return actual,defective
  def computeB(i):
 #all the rows associated with this rule will be predicted as defective.
 #then calculate pd,pf, efforts.
 #efforts is normalized
    FP, TP,Loc = 0,0,0,
    for row in i.rows:
      Loc += row[10] # this is loc, # 10
      if row[-1]==0:
        FP += 1
      else:
        TP += 1
    pd = TP/the.NP.defective
    pf = FP/the.NP.nondefective
    effort = Loc/the.effortNorm.Total[10]# this is normalized effort
    alpha = the.RULER.rules.alpha
    beta = the.RULER.rules.beta
    gamma = the.RULER.rules.gamma
    B = (pd**2*alpha +(1-pf)**2*beta\
        +(1-effort)**2*gamma)**0.5/(alpha+beta+gamma)**0.5
    # pdb.set_trace()
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
  def one(lst,attr, x = lambda z: z[col]):
    i, dist = 0, int(math.ceil(len(lst)/N))
    cut,out = [],[]
    while True:
      if i+dist <len(lst):
        cut +=[lst[i:i+dist]]
        i = i+dist
      else:
        # cut[-1].extend([lst[i:]])
        cut +=[lst[i:]]
        break
    for sub in cut:
      out +=[Range(attr = attr, x = o(lo = x(sub[0]), hi = x(sub[-1])), rows = sub)]
    return out
  # def divide(lst,n,attr,x = lambda z:z(col)):
  #   '''
  #   recursively divide
  #   '''
  #   out = []
  #   if n > N:
  #     return None
  #   cut = [lst[:int(n/2)],lst[int(n/2):]]
  #   n +=1
  #   return cut,n
  # def recursive(lst,n):
  #   cut,i = divide(lst,n)
  #   if cut:
  #     recursive(cut[0],i+1)
  #     recursive(cut[1],i+1)
  #   else:
  #     out +=[Range(attr = attr, x = o(lo = x(cut[0]), hi = x(cut[-1])), rows = cut)]
  #   return out
  result = []
  for col in t.indep:
    result +=one(sorted(t.data, key = lambda x:x[col]), attr = t.names[col])
  return result



  pass

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
