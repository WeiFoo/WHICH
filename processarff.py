from __future__ import division, print_function
import sys, pdb,random,math,os,shutil
from os import listdir
from os.path import isfile, join
import numpy as np


def All(src= "../DATASET",folds = 3):
  def clearFiles():
    folders0 = [ join(src,f) for f in listdir(src) if not isfile(join(src,f))]
    folders = [ join(src,f)for f in listdir(folders0) if not isfile(join(folders0,f))]
    pdb.set_trace()
    for f in folders:
      for ff in listdir(f):
        if isfile(join(f,ff)):
          os.remove(join(f,ff))
  def mergeall(data,k):
    out =[]
    for z in range(folds):
      if z != k:
        out += data[z]
    # out.extend(data[z] for z in range(folds) if z!=k)
    return out

  def tuning(data, k=3):
    dist = len(data)
    random.shuffle(data)
    cut = int(dist/k)
    tune = data[-cut:]
    train = data[:-cut]
    return (tune,train)

  def writefile(newfile,newcontent,arff = True):
    f = open(newfile,"w")
    content = newcontent if not arff else "@relation "+ newcontent
    f.write(content)
    f.close()

  def generate(srcs, dealKC3 = False):
    # def isSatisfied():
    #   for fold in csvout:
    #     has_Defective = False
    #     for line in fold:
    #       if line[-2] == "1":
    #         has_Defective = True
    #         break
    #     if not has_Defective:
    #       return False
    #   return True
    def csv2arff(csvfile):
      arfffile = []
      for line in csvfile:
        if line[-2]=="1": line=line[:-2]+ "true\n" #'str' object does not support item assignment
        if line[-2]=="0": line=line[:-2]+ "false\n"
        arfffile +=[line]
      return arfffile

    arffcontent =[]
    for _ in range(10): random.shuffle(csvcontent) # each time shuffle the data
    # for line in csvcontent:
    #     if line[-2]=="1": line=line[:-2]+ "true\n" #'str' object does not support item assignment
    #     if line[-2]=="0": line=line[:-2]+ "false\n"
    #     arffcontent +=[line]
    last, dist, csvout, arffout = 0, int(math.ceil(len(csvcontent) / folds)), [], []
    cut = [(j + 1) * dist for j in range(folds) if (j + 1) * dist < len(csvcontent)]
    cut.extend([len(csvcontent)])
    for k in cut:
      csvout.extend([csvcontent[last:k]])  # divide the data into N folds
      # arffout.extend([arffcontent[last:k]])
      last = k
    # if not isSatisfied():
    #   pdb.set_trace()
    #   return False # if False, we need to regenerate the data.
    for k in range(folds):
      csvtest = csvout[k]
      writefile(srcs+"/csv/test"+str(k)+".csv",",".join(csvheader) +"".join(csvtest))
      csvtrain = mergeall(csvout,k)
      newcsvtune, newcsvtrain = tuning(csvtrain)
      writefile(srcs+"/csv/train"+str(k)+".csv",",".join(csvheader) +"".join(newcsvtrain))
      writefile(srcs+"/csv/tune"+str(k)+".csv",",".join(csvheader) +"".join(newcsvtune))
      arfftest = csv2arff(csvtest)
      writefile(srcs+"/arff/test"+str(k)+".arff", name+"\n\n"+"".join(arffheader)+"\n"+"".join(arfftest))
      newarfftrain = csv2arff(newcsvtrain)
      newarfftune = csv2arff(newcsvtune)
      writefile(srcs+"/arff/train"+str(k)+".arff", name+"\n\n"+"".join(arffheader)+"\n"+"".join(newarfftrain))
      writefile(srcs+"/arff/tune"+str(k)+".arff", name+"\n\n"+"".join(arffheader)+"\n"+"".join(newarfftune))

  files = [ join(src,f) for f in listdir(src) if isfile(join(src,f)) and "py" not in f and "DS" not in f]
  folders = [f[:f.find(".")] for f in listdir(src) if isfile(join(src,f)) and "py" not in f and "DS" not in f]
  name = ""
  for j,one in enumerate(files[:]):
    srcs =src+'/'+folders[j]
    if os.path.exists(srcs):
      shutil.rmtree(srcs)
    os.makedirs(srcs +'/arff/') # generate new folders for each file
    os.makedirs(srcs +'/csv/') # generate new folders for each file
    f = open(one, "r")
    csvcontent,arffcontent,csvheader,arffheader  = [],[],[],[]
    while True:
      line = f.readline()
      if not line:
        break
      elif "%" in line or len(line) == 1 :
        continue
      elif "relation" in line:
        name = line[10:-1]
        print("*****"+name+"+++++")
        continue
      elif "@" in line:
        arffheader += [line]
        if "data" in line:
          continue
        if "defects" in line:
          csvheader += ["$<defects\n"]
        else:
          csvheader +=["$"+line[line.find("e")+2:line.find("numberic")-8]]
      else:
        if len(line) <10:
          continue
        if "?" in line:
          continue
        if line[-1] !="\n":
          line+="\n"
        if "false" in line:
          line = line.replace("false","0")
        if "no" in line:
          line = line.replace("no","0")
        if "yes" in line:
          line = line.replace("yes","1")
        if "true" in line:
          line = line.replace("true","1")
        csvcontent +=[line]
    generate(srcs)


def arffs(src= "../DATASET",folds = 3):
  data = arff.load(open(src+"/cm1.arff","rb"))
  dataset = np.array(data["data"])
  print(dataset)
if __name__ == "__main__":
  All()