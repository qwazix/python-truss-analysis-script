'''
Created on 10/01/2011

@author: 04610922479
'''
import random, math
from nsga2 import Solution
from nsga2 import NSGAII
import pickle
import json
import collections
#import trussanalysisscript.py
import subprocess
from random import randint

#from nsga2.nsga2 import Solution

class T1Solution(Solution):
    '''
    Solution for the T1 function.
    '''
    def __init__(self,items):
        '''
        Constructor.
        '''
        Solution.__init__(self, 2)
        
        self.items = items
        
        self.evaluate_solution()
        
    def evaluate_solution(self):
        '''
        Implementation of method evaluate_solution() for T1 function.
        '''
        print "*************"
        x=str(randint(1,9))
        subprocess.Popen("python /home/qwazix/Documents/projects/python-truss-analysis-script/src/trussanalysisscript.py /home/qwazix/Documents/projects/python-truss-analysis-script/src/data"+x+".json",shell=True)
        
        my_dict= {}
        try:
            f = open('/home/qwazix/Documents/projects/python-truss-analysis-script/src/myfile.pkl','rb')
            my_dict=pickle.load(f)
            f.close()
            totalWeight=my_dict['totalWeight'];
            totalValue=my_dict['displacements'][2];
            print totalValue
        #totalWeight=0.0;
        #totalValue=0.0
        #for i in self.items:
            #totalValue += i[0]
            #totalWeight += i[1]
            
            self.objectives[0] = totalValue
            self.objectives[1] = totalWeight
        except IOError:
            self.objectives[0] = 0
            self.objectives[1] = 0
        except EOFError:
            self.objectives[0] = 0
            self.objectives[1] = 0
            
            
        
    def crossover(self, other):
        '''
        Crossover of T1 solutions.
        '''
        print self.items
        child_items = []
        for i in range(len(self.items)):
            #print i
            if i <= len(self.items)/2:
                child_items.append(other.items[i])
            else:
                child_items.append(self.items[i])

        child_solution = T1Solution(child_items)        
        
        return child_solution
    
    def mutate(self):
        '''
        Mutation of T1 solution.
        '''
        itemList = []
        loop=0;
        data={}
        for loop in xrange(0,10):
            stringLoop=str(loop)
            file = open('/home/qwazix/Documents/projects/python-truss-analysis-script/src/data'+stringLoop+'.json', 'r')
            data[loop] = json.load(file,object_pairs_hook=collections.OrderedDict)['truss']
            loop=loop+1;
            file.close();
        
        itemList.append(data[0])
        itemList.append(data[1])
        itemList.append(data[3])
        itemList.append(data[4])
        itemList.append(data[5])
        itemList.append(data[6])
        itemList.append(data[7])
        self.items[random.randint(0,2)] = itemList[random.randint(0,len(itemList)-1)]

    
if __name__ == '__main__':
    nsga2 = NSGAII(2, 0.1, 1.0)

    loops=10;
    loop=0;
    for loop in xrange(0,10):
        stringLoop=str(loop)
        print "+++++++++++++"
        file = open('/home/qwazix/Documents/projects/python-truss-analysis-script/src/10th-series.json', 'r')
        truss = json.load(file,object_pairs_hook=collections.OrderedDict)['truss']
        #truss3=json.loads(file,object_pairs_hook=collections.OrderedDict)
        joints = list()
        i=0
        for id, j in truss['joints'].iteritems():
            print j
            if not "supports" in j:
                oldY=j['y'];
                id2=str(i)
                newY=random.uniform(oldY+1,oldY-1)
                truss['joints'][id2]['y']=newY
            i=i+1
            print Solution;
        #newtruss=truss
        newtruss=dict({'truss':truss})
        file2 = open('/home/qwazix/Documents/projects/python-truss-analysis-script/src/data'+stringLoop+'.json', 'w+')
        file2.write(json.dumps(newtruss))
        #file2.write(json.dumps(newtruss))
        file2.close();
                

        file.close();
        loop=loop+1

    loop=0;
    data={}
    for loop in xrange(0,10):
        stringLoop=str(loop)
        file = open('/home/qwazix/Documents/projects/python-truss-analysis-script/src/data'+stringLoop+'.json', 'r')
        data[loop] = json.load(file,object_pairs_hook=collections.OrderedDict)['truss']
        loop=loop+1;
        file.close();
    
    item1 = data[0]
    item2 = data[1]
    item3 = data[2]
    item4 = data[3]
    item5 = data[4]
    item6 = data[5]
    item7 = data[6]
    
    P = []
    P.append(T1Solution([item1,item2,item5]))#32,7
    P.append(T1Solution([item3,item1,item7]))#42,23
    P.append(T1Solution([item2,item3,item5]))
    P.append(T1Solution([item1,item6,item3]))
    P.append(T1Solution([item7,item1,item2]))
    P.append(T1Solution([item4,item3,item1]))
    
    #for i in range(500):
        #P.append(T1Solution())
    #for j in range(len(P)):
        #print P[j].items
        
    nsga2.run(P, 10, 5)

    #for j in range(len(P)):
        #print P[j].items
    
    csv_file = open('tmp/nsga2_out.txt', 'w')
    for i in range(len(P)):
        csv_file.write("" + str(P[i].objectives[0]) + ", " + str(P[i].objectives[1]) + "\n")
        
    csv_file.close()
