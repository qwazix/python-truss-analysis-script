#!/usr/bin/python
# coding=utf-8
import sys

# To change this template, choose Tools | Templates
# and open the template in the editor.

from cmath import sqrt
import array
from numpy import *
import scipy
import json

__author__="qwazix"
__date__ ="$Jan 12, 2013 2:52:56 PM$"

class truss:
    beams = list()
    joints = list()
    def __init__(self, filename):
        # @type file file
        file = open(filename, 'r')
        truss = json.load(file)['truss']
        self.joints = list()
        for id, j in truss['joints'].iteritems():
            # @type newJoint joint
            newJoint = joint(int(id),j["x"],j["y"])
            if "loads" in j:
                tmpLoads = list()
                for l in j["loads"]:
                    tmpLoads.append(load(l["direction"],l["magnitude"]))
                    newJoint.loads = tmpLoads
            if "supports" in j:
                tmpSupports = list()
                for s in j["supports"]:
                    tmpSupports.append(support(s["direction"],s["prescribedDisplacement"]))
                    newJoint.supports = tmpSupports
            self.joints.append(newJoint)

        self.beams = list()
        for id, b in truss['beams'].iteritems():
            # @type newBeam beam
            newBeam = beam(int(id),self.joints[b["start"]],self.joints[b["end"]])
            newBeam.elasticity = b["elasticity"]
            newBeam.sectionArea = b["area"]
            self.beams.append(newBeam)
    

class point:
    x = 0
    y = 0
    def __init__(self, x=0,y=0):
       self.x = x
       self.y = y
    def distance(self, point):
        return sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2))
    def __add__(self, p):
        return point(self.x+p.x, self.y+p.y);
    def __sub__(self, p):
        return point(self.x-p.x, self.y-p.y);
    def __str__(self):
        return str(self.x) + "," + str(self.y)

class joint:
    id
    coordinates = point() # Δίνουμε τα χαρακτηριστικά της κλάσης
    supports = list()
    displacement = point()
    loads = list()
    totalMagnitude = point()
    def __init__(self, id, x, y):
        self.id = id
        self.coordinates = point(x,y)
    def __str__(self):
        res= "\n"
        res+= "JOINT\n"
        res+= "---------\n"
        res+= 'Joint No:      %d\n' % self.id;
        res+= '       x:      %d\n' % self.coordinates.x;
        res+= '       y:      %d\n' % self.coordinates.y;
        for l in self.loads:
            # @type load load
            res += l.__str__()
        for s in self.supports:
            # @type load load
            res += s.__str__()
        return res

class load:
    direction = "x"
    magnitude = 0
    def __init__(self, direction, magnitude):
        self.direction = direction
        self.magnitude = magnitude
    def __str__(self):
        res= "\n"
        res+= "LOAD\n"
        res+= "---------\n"
        res+= 'direction:      %s\n' % self.direction;
        res+= 'magnitude:      %d\n' % self.magnitude;
        return res

class support:
    direction = "x"
    displacement = 0
    def __init__(self, direction, displacement):
        self.direction = direction
        self.displacement = displacement
    def __str__(self):
        res= "\n"
        res+= "SUPPORT\n"
        res+= "---------\n"
        res+= 'direction:      %s\n' % self.direction;
        res+= 'displacement:      %d\n' % self.displacement;
        return res


class beam:
    id = 0
    startNode = 0
    endNode = 0
    sectionArea = 0.002
    elasticity = 2e11
    distances = point()
    length = 0
    sin = 0
    cos = 0
    ktemp = matrix(0)
    klocal = zeros((4,4))
    T = matrix(0)
    kglobal = matrix(0)
    def __init__(self, id, start, end):
        # @type start joint
        # @type end joint

        #scipy for matlab users http://www.scipy.org/NumPy_for_Matlab_Users
        self.id = id
        self.startNode = start
        self.endNode = end
        self.distances = end.coordinates - start.coordinates
        self.length = start.coordinates.distance(end.coordinates)
        self.sin = self.distances.y/self.length
        self.cos = self.distances.x/self.length
        self.ktemp = self.sectionArea*self.elasticity/self.length * mat("1 0;0 0")
#        self.klocal = self.ktemp
        for i in range(4):
            for j in range(4):
                #βάζουμε τον πίνακα ktemp 4 φορές στον πίνακα klocal ως εξής
                # __________
                #|  1 |  2 | --> klocal
                #|____|____|  /
                #|  3 |  4 | /
                #|____|____|
                self.klocal[i,j] = self.ktemp[i%2,j%2]
        #build transformation matrix
        self.T = array([[self.cos, self.sin, 0, 0],[-self.sin, self.cos, 0, 0],[0, 0, self.cos, self.sin],[0, 0, -self.sin, self.cos]])
        #compute stiffness matrix in global coords
        self.kglobal=(self.T).T.dot(self.klocal).dot(self.T)
    def __str__(self):
        res= "\n"
        res+= "BEAM\n"
        res+= "---------\n"
        res+= 'Beam No:      %d\n' % self.id;
        res+= 'Length:       %d\n' % self.length;
        res+= 'Elasticity:   %.1e\n' % self.elasticity;
        res+= 'Section Area: %d\n' % self.sectionArea;
        res+= 'cos:          %d\n' % self.cos;
        res+= 'sin:          %d\n' % self.sin;
        res+= 'start:        joint  %d\n' % self.startNode.id;
        res+= 'end:          joint  %d\n' % self.endNode.id;
        return res;

def addToGeneral(generalK, b):
    # @type b beam
    startC=2*b.startNode.id
    endC=2*b.endNode.id
    for i in range(2):
        for j in range(2):
            generalK[startC+i,startC+j]=b.kglobal[i,j]
            generalK[startC+i,endC+j]=b.kglobal[i,2+j]
            generalK[endC+i,startC+j]=b.kglobal[2+i,j]
            generalK[endC+i,endC+j]=b.kglobal[2+i,2+j]
    return generalK

def computeAxialForces(b, u):
    # @type b beam
    myu = array();
    myu[i,0]=u[2*b.startNode.id-1,1]
    myu[i,0]=u[2*b.startNode.id,1]
    myu[i,0]=u[2*b.endNode.id-1,1]
    myu[i,0]=u[2*b.endNode.id,1]
    return b.klocal.dot(b.T).dot(myu);

    

if __name__ == "__main__":

    # @type myTruss truss
    myTruss = truss(sys.argv[1])




    for b in myTruss.beams:
        print b

    for j in myTruss.joints:
        print j

#    n1 = joint(0,0,0)
#    n2 = joint(1,0,1)
#
#    myBeam = beam(1, n1, n2)
#
#    print myBeam
