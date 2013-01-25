#!/usr/bin/python
# coding=utf-8
import sys

# To change this template, choose Tools | Templates
# and open the template in the editor.

from cmath import sqrt
from numpy import *
import scipy
import json
import math

__author__="qwazix"
__date__ ="$Jan 12, 2013 2:52:56 PM$"

class truss:
    beams = list()
    joints = list()
    supportedDof = 0
    dof = 0
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
            if ("supports" in j) : newJoint.supports = j["supports"]
            self.joints.append(newJoint)

        self.dof = zeros((len(self.joints)*2))
        self.dofArray();
        self.beams = list()
        for id, b in truss['beams'].iteritems():
            # @type newBeam beam
            newBeam = beam(int(id),self.joints[b["start"]],self.joints[b["end"]])
            newBeam.elasticity = b["elasticity"]
            newBeam.sectionArea = b["area"]
            self.beams.append(newBeam)

    def calculateSupportedDof(self):
        sDof = 0
        for j in self.joints:
            # @type j joint
            sDof += len(j.supports);
        self.supportedDof = sDof;

    def dofArray(self):
        sDof = 0
        for j in self.joints:
            # @type j joint
            if "x" in j.supports:
                self.dof[sDof] = 1
                sDof += 1
            if "y" in j.supports:
                self.dof[sDof] = 1
                sDof += 1
        self.supportedDof = sDof;

    

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
    supports = dict()
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
    def getTotalLoadMagnitude(self):
        self.totalMagnitude = point();
        for l in self.loads:
            # @type l load
            if l.direction == "x":
                self.totalMagnitude.x += l.magnitude
            else:
                self.totalMagnitude.y += l.magnitude
        return self.totalMagnitude

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
        self.kglobal=(self.T).conj().transpose().dot(self.klocal).dot(self.T)
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
            generalK[startC+i,startC+j]+=b.kglobal[i,j]
            generalK[startC+i,endC+j]+=b.kglobal[i,2+j]
            generalK[endC+i,startC+j]+=b.kglobal[2+i,j]
            generalK[endC+i,endC+j]+=b.kglobal[2+i,2+j]


def computeAxialForces(b, u):
    # @type b beam
    myu = array();
    myu[i,0]=u[2*b.startNode.id-1,1]
    myu[i,0]=u[2*b.startNode.id,1]
    myu[i,0]=u[2*b.endNode.id-1,1]
    myu[i,0]=u[2*b.endNode.id,1]
    return b.klocal.dot(b.conj().transpose()).dot(myu);

def getColumn(mat, column):
    return array([mat[:][:,column]]).transpose()


if __name__ == "__main__":

    set_printoptions(precision=4)
    set_printoptions(linewidth=150)
    # @type myTruss truss
    myTruss = truss(sys.argv[1])

    kGeneral = zeros((2*len(myTruss.joints),2*len(myTruss.joints)))
    for b in myTruss.beams:
        addToGeneral(kGeneral, b)
    print "kGeneral"
    print kGeneral

    dof = len(myTruss.joints)*2
    supportedDof = myTruss.supportedDof;
    freeDof = dof - myTruss.supportedDof;

    kff = zeros((freeDof,freeDof))
    ksf = zeros((supportedDof,freeDof))
    kfs = zeros((freeDof,supportedDof))
    kss = zeros((supportedDof,supportedDof))

    ffi = 0
    sfi = 0
    fsi = 0
    ssi = 0
    sxj = 0
    fxj = 0

    for i in range(dof): #we take a row
        if myTruss.dof[i]: #if this row is supported
            for j in range(dof): #for each item in the rwo
                if myTruss.dof[j]: #if the column is supported
                    print kss
                    kss[ssi,sxj]=kGeneral[i,j] #we fill kss
                    ssi += 1 #and go to next empty cell
                else:
                    ksf[sfi,sxj]=kGeneral[i,j] #we fill ksf
                    sfi += 1 #and go to the next empty cell
            sxj +=1; #when an s row is finished we know
                #that we filled the first row of both ksf and kss
            ssi = 0; sfi = 0 #and start over with the rows
        else:
            for j in range(dof):
                if myTruss.dof[j]:
                    kfs[fsi,fxj]=kGeneral[i,j]
                    fsi += 1
                else:
                    kff[ffi,fxj]=kGeneral[i,j]
                    ffi += 1
            fxj += 1;
            fsi=0; ffi=0

    print "kff"
    print kff
    print "kss"
    print kss
    print "kfs"
    print kfs
    print "ksf"
    print ksf

# build xf
#----------------------------
#build xfful (preliminary for reducing to xf)
    rf = zeros((freeDof))
    fi = 0
    for j in myTruss.joints:
        if not "x" in j.supports:
            rf[fi]= j.getTotalLoadMagnitude().x; #total load magnitudes haven't been
            fi += 1                                     #initialized
        if not "y" in j.supports:
            rf[fi]= j.totalMagnitude.y;#now the values of total magnitude are
            fi += 1                    #already stored in the variables so no need
                                       #to calculate again
    print rf



#print myTruss.dof

#    for b in myTruss.beams:
#        print b
#
#    for j in myTruss.joints:
#        print j

#    n1 = joint(0,0,0)
#    n2 = joint(1,0,1)
#
#    myBeam = beam(1, n1, n2)
#
#    print myBeam
