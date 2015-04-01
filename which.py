#__author__ = 'WeiFu'
from __future__ import print_function, division
import sys,pdb
from ruler import *
from table import *
def csv(f= "./data/ant/ant-1.5copy.csv"):
  t = table(f)
  n = [ header.name for header in t.headers]
  d = [ row.cells for row in t._rows]
  pdb.set_trace()
  return data(names= n, data = d)

def _range():
  LIB(seed=1)
  RULER(tiny=4)
  def _ranges():
    for z in ranges(csv()): print(z)
  run(_ranges)
def _rule():
  LIB(seed=1)
  RULER(tiny=4,better=gt)
  def _ruler():
    t=csv()
    print(t.score, "baseline :",len(t.data))
    for z in ruler(t):
      print(z.score,z)
  run(_ruler)

if __name__ == "__main__":
  _rule()