from __future__ import division, print_function
import sys, pdb,random,math,os,shutil
from os import listdir
from os.path import isfile, join
import arff
import numpy as np

def sperateData(src= "./", percent = 0.2):
  def clearFiles():
    pdb.set_trace()
    folders = [ join(src,f) for f in listdir(src) if not isfile(join(src,f))]
    for f in folders:
      for ff in listdir(f):
        if isfile(join(f,ff)):
          os.remove(join(f,ff))

  def generate():
    clearFiles()
    pdb.set_trace()
    sample_Len = int(len(csvcontent)*percent)
    pdb.set_trace()
    test = random.sample(arffcontent,sample_Len)
    train = random.sample(arffcontent,len(arffcontent)-sample_Len)
    print("slsl")
    # pdb.set_trace()
    arff = open("./newarff/"+name+"test.arff","w")
    arfftest = "@relation "+name+"\n\n"+"".join(arffheader)+"\n"+"".join(test)
    arff.write(arfftest)
    arff.close()
    arff = open("./newarff/"+name+"train.arff","w")
    arfftrain = "@relation "+name+"\n\n"+"".join(arffheader)+"\n"+"".join(train)
    arff.write(arfftrain)
    arff.close()

    test = random.sample(csvcontent,sample_Len)
    train = random.sample(csvcontent,len(arffcontent)-sample_Len)
    csvf = open("./newcsv/"+name+"test.csv","w")
    csvtest = ",".join(csvheader) +"".join(test)
    csvf.write(csvtest)
    csvf.close()
    csvf = open("./newcsv/"+name+"train.csv","w")
    csvtrain = ",".join(csvheader) +"".join(train)
    csvf.write(csvtrain)
    csvf.close()







  files = [ join(src,f) for f in listdir(src) if isfile(join(src,f)) and "py" not in f]
  for one in files[:]:
    f = open(one, "r")
    name = ""
    csvheader,arffheader, csvcontent, arffcontent  = [],[],[],[]
    while True:
      line = f.readline()
      if not line:
        break
      elif "%" in line or len(line) == 1 :
        continue
      elif "relation" in line:
        name = line[10:-1]
        # print("*****"+name+"+++++")
      elif "@" in line:
        arffheader += [line]
        if "data" in line:
          continue
        if "defects" in line:
          csvheader += ["$<defects\n"]
        else:
          csvheader +=["$"+line[line.find("e")+2:line.find("numberic")-8]]
      else:
        if len(line) == 2:
          continue
        if line[-1] !="\n":
          line+="\n"
        arffcontent +=[line]
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
    generate()

def All(src= "/Users/WeiFu/Github/DATASET",folds = 3):
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

  def generate(srcs):
    def writefile(newfile,newcontent,arff = True):
      f = open(newfile,"w")
      content = newcontent if not arff else "@relation "+ newcontent
      f.write(content)
      f.close()
    # clearFiles()
    random.shuffle(csvcontent) # each time shuffle the data
    random.shuffle(arffcontent)
    last, dist, csvout, arffout = 0, int(math.ceil(len(csvcontent) / folds)), [], []
    cut = [(j + 1) * dist for j in range(folds) if (j + 1) * dist < len(csvcontent)]
    cut.extend([len(csvcontent)])
    for k in cut:
      csvout.extend([csvcontent[last:k]])  # divide the data into N folds
      arffout.extend([arffcontent[last:k]])
      last = k
    for k in range(folds):
      writefile(srcs+"/arff/test"+str(k)+".arff", name+"\n\n"+"".join(arffheader)+"\n"+"".join(arffout[k]))
      arfftrain = mergeall(arffout,k)
      writefile(srcs+"/arff/train"+str(k)+".arff", name+"\n\n"+"".join(arffheader)+"\n"+"".join(arfftrain))
      writefile(srcs+"/csv/test"+str(k)+".csv",",".join(csvheader) +"".join(csvout[k]))
      csvtrain = mergeall(csvout,k)
      writefile(srcs+"/csv/train"+str(k)+".csv",",".join(csvheader) +"".join(csvtrain))

  files = [ join(src,f) for f in listdir(src) if isfile(join(src,f)) and "py" not in f and "DS" not in f]
  folders = [f[:f.find(".")] for f in listdir(src) if isfile(join(src,f)) and "py" not in f and "DS" not in f]
  srcs = ""
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
      elif "@" in line:
        arffheader += [line]
        if "data" in line:
          continue
        if "defects" in line:
          csvheader += ["$<defects\n"]
        else:
          csvheader +=["$"+line[line.find("e")+2:line.find("numberic")-8]]
      else:
        if "?" in line:
          continue
        if line[-1] !="\n":
          line+="\n"
        if "yes" in line:
          line = line.replace("yes","true")
        if "no" in line:
          line = line.replace("no","false")
        if line[-2]=="1": line=line[:-2]+ "true\n" #'str' object does not support item assignment
        if line[-2]=="0": line=line[:-2]+ "false\n"
        arffcontent +=[line]
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


def arffs(src= "/Users/WeiFu/Github/DATASET",folds = 3):
  data = arff.load(open(src+"/cm1.arff","rb"))
  dataset = np.array(data["data"])
  print(dataset)
if __name__ == "__main__":
  All()