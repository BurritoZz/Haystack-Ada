# Do a replace of a HelloWorld in ADA language:
from os import replace
import libadalang as lal
import argparse
import re
import fileinput
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--project', '-P', type=str)
parser.add_argument('files', help='Files to analyze', type=str, nargs='+')
args = parser.parse_args()

provider = None
if args.project:
    provider = lal.UnitProvider.for_project(args.project)
context = lal.AnalysisContext(unit_provider=provider)

slock_range = []
n_line = 0
data = dict()
filename = args.files[0]

def createHashMap():
    for filename in args.files:
        unit = context.get_from_file(filename)
        print("==== {} ====".format(filename))
        for d in unit.diagnostics:
            print("{}: {}".format(filename, d))
        # print("### All Object Declaration called in the: {}".format(filename))
        for node in unit.root.findall(lal.ObjectDecl):
            # print("--> Line {}: {}".format(node.sloc_range.start.line, repr(node.text)))
            data.update({str(node.sloc_range):node.text})
            slock_range.append(str(node.sloc_range))
            for child in node.children:
                if(child != None):
                    if(child.text == ''):
                        pass
                    else:
                        data.update({str(child.sloc_range):child.text})
                        slock_range.append(str(child.sloc_range))
        # print("### All call expression called in the: {}".format(filename))
        for call in unit.root.findall(lal.CallExpr):
            # print("--> Line {}: {}".format(call.sloc_range.start.line, repr(call.text)))
            for child in call.children:
                if(child != None):
                    if(child.text == ''):
                        pass
                    else:
                        data.update({str(child.sloc_range):child.text})
                        slock_range.append(str(child.sloc_range))
        # Cleaning the data dictionary of empty value:
        # d = dict( [(k,v) for k,v in data.items() if len(v)>0])
    print("All the things that i found:")
    print(data)
    return data
# createHashMap()

def returnSlock():
    return slock_range

# Cleaning all the list+dict:
def cleaningStuff():
    data.clear()
    slock_range.clear()

# Return a list of int in this way : [line,start,end]
def startEnd(y):
    slot = []
    for f in range(len(y)):
        tmp_list = []
        str_range = y[f]
        line = re.search('(\d+):',str_range)
        tmp_list.append(int(line.group(1)))
        k = str_range.split("-")
        # print(k)
        for x in range(len(k)):
            se = re.search('\:(.*)$', k[x]) #se = Start End
            k[x] = int(se.group(1))
            tmp_list.append(k[x])
        slot.append(tmp_list)
    return slot
# print("Slock function output: "+str(startEnd(slock_range)))

def startEndString(y):
    u = []
    str_range = y
    k = str_range.split("-")
    line = re.search('(\d+):',k[0])
    u.append(int(line.group(1)))
    for v in k:
        tmp = re.search('\:(.*)$', v)
        u.append(int(tmp.group(1)))
    return u

slock__ = tuple(startEnd(slock_range))

# Return a Dictionary in this way: {'[line,start,end]': 'declaration', ... }
def hashFinal(hashMap):
    i = 0
    # hashMap = {'6:4-6:12': 'Put_Line', '6:14-6:27': '"Hello World"', '8:7-8:15': 'Put_Line', '8:16-8:48': '"We are in the first half year."'}
    for k in list(hashMap):
        hashMap[str(slock__[i])] = hashMap.pop(k)
        i += 1
    return hashMap

# Return a list of each Line found [1,2,3, ...]
def getLine(hashMap):
    lineList = []
    for key in hashMap.keys():
        lineList.append(int(key[1]))
    return lineList

# Get back all the equals line of a declaration -> useful in the future to replace an entire line
# return line list or None (if no equal lines)
def foundEqualLine(list):
    line = []
    s = set([x for x in list if list.count(x) > 1])
    for i in s:
        line.append(int(i))
    line.reverse()
    if(len(line) > 0):
        return line
    else:
        return

def replace_line(filename,n_line,start,text,end):
        lines = open(filename, 'r').readlines()
        dec = int(input("Make a choice: [1 = replace bottom up, Any other numer = exit] "))
        if(dec == 1):
            toChange = lines[n_line-1] 
            toChange = toChange[0:start-1] + text + '\n'
            print(toChange)
            lines[n_line-1] = toChange
            out = open(filename, 'w')
            out.writelines(lines)
            out.close()
        elif(dec == 2):
            toChange = lines[n_line-1]
            toChange = toChange[0:start-1] + text + toChange[end-1:]
            print(toChange)
            lines[n_line-1] = toChange
            out = open(filename, 'w')
            out.writelines(lines)
            out.close()

# Function to replace an entire peace of file (ex: for loop)
def replace_body(filename,start,end,replacelines:list,startChar):
    # replacelines = ["Put_Line(firstLine);\n","Put_Line(secondLine);\n","Put_Line(thirdLine);\n"]
    with open(filename, "r") as infile:
        lines = infile.readlines()
    with open(filename, "w") as outfile:
        counter = 0
        # print(start,end)
        for pos, line in enumerate(lines):
            if(pos == start):
                lines[start-1] = lines[start-1][0:startChar-1] + replacelines[counter]
                start = start + 1 
                counter = counter +1
            if(start == end+1):
                break
        outfile.writelines(lines)

# replace_body(filename,3,5,"Text")
# Execution:
# replace_strings(filename)