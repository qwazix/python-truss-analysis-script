#!/usr/bin/python
'''
Created on 10/01/2011

@author: 04610922479
'''
import random, math
from nsga2 import Solution
from nsga2 import NSGAII
import json
import collections
import sys
from trussanalysisscript import truss


#from nsga2.nsga2 import Solution

class T1Solution(Solution):
    '''
    Solution for the T1 function.
    '''
    def __init__(self):
        '''
        Constructor.
        '''
        Solution.__init__(self, 2)
        
        self.xmin = 0.0
        self.xmax = 1.0
        file = open(sys.argv[1], 'r')
        trussDict = json.load(file,object_pairs_hook=collections.OrderedDict)['truss']

        for id,joint in trussDict['joints'].iteritems():
            if not "supports" in joint or not "y" in joint["supports"]:
                joint["y"] = random.uniform(joint["y"]-1,joint["y"]+1)


        self.myTruss = truss(trussDict)
        
        self.evaluate_solution()
        
    def evaluate_solution(self):
        '''
        Implementation of method evaluate_solution() for T1 function.
        '''
        self.myTruss.solve()
        self.objectives[0] = self.myTruss.displacements[5]
        
        
        self.objectives[1] = self.myTruss.totalWeight
        
    def crossover(self, other):
        '''
        Crossover of T1 solutions.
        '''
        child_solution = T1Solution()
        
        for i in range(len(self.myTruss.joints)):
#            if i<=len(self.myTruss.joints)/2:
            child_solution.myTruss.joints[i].coordinates.y = (self.myTruss.joints[i].coordinates.y + other.myTruss.joints[i].coordinates.y)/2
        
        return child_solution
    
    def mutate(self):
        '''
        Mutation of T1 solution.
        '''
        condition = True
        while condition:
            joint = self.myTruss.joints[random.randint(0, len(self.myTruss.joints)-1)]
            if not "y" in joint.supports:
                joint.coordinates.y = random.uniform(joint.coordinates.y -3, joint.coordinates.y+3)
                condition = False

    
if __name__ == '__main__':
    nsga2 = NSGAII(2, 0.1, 1.0)
    
    P = []
    for i in range(50):
        P.append(T1Solution())
    
    nsga2.run(P, 5, 2)
#    nsga2.run(P, 50, 20)
    
    csv_file = open('/tmp/nsga2_out.csv', 'w')
    
    for i in range(len(P)):
        csv_file.write("" + str(P[i].objectives[0]) + ", " + str(P[i].objectives[1]) + "\n")
        
    csv_file.close()
