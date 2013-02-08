#!/usr/bin/python
# coding=utf-8
import sys

# To change this template, choose Tools | Templates
# and open the template in the editor.

from cmath import sqrt
from numpy import *
#import scipy
import json
import math
import collections

__author__="qwazix"
__date__ ="$Jan 12, 2013 2:52:56 PM$"

class truss:
    beams = list()
    joints = list()
    supportedDof = 0
    dof = 0
    kGeneral = 0
    freeDof =0
    dofCount = 0
    def __init__(self, filename):
        # @type file file
        file = open(filename, 'r')
        truss = json.load(file,object_pairs_hook=collections.OrderedDict)['truss']
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
        self.kGeneral = zeros((2*len(self.joints),2*len(self.joints)))
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
        self.dofCount = len(self.joints)*2
        self.freeDof = self.dofCount - self.supportedDof;

    def dofArray(self):
        sDof = 0
        i = 0
        for j in self.joints:
            # @type j joint
            if "x" in j.supports:
                self.dof[i] = 1
                sDof += 1
            i += 1
            if "y" in j.supports:
                self.dof[i] = 1
                sDof += 1
            i += 1
        self.supportedDof = sDof;

    def addToGeneral(self, b):
        # @type b beam
        startC=2*b.startNode.id
        endC=2*b.endNode.id
        for i in range(2):
            for j in range(2):
                self.kGeneral[startC+i,startC+j]+=b.kglobal[i,j]
                self.kGeneral[startC+i,endC+j]+=b.kglobal[i,2+j]
                self.kGeneral[endC+i,startC+j]+=b.kglobal[2+i,j]
                self.kGeneral[endC+i,endC+j]+=b.kglobal[2+i,2+j]


    def computeAxialForces(self, b, u):
        # @type b beam
        myu = zeros((4));
        myu[0]=u[2*b.startNode.id]
        myu[1]=u[2*b.startNode.id+1]
        myu[2]=u[2*b.endNode.id]
        myu[3]=u[2*b.endNode.id+1]
        myu = array([myu]).transpose()
    #    print (b.klocal.dot(b.T)).dot(myu)
        return (b.klocal.dot(b.T)).dot(myu);

    def getColumn(self, mat, column):
        return array([mat[:][:,column]]).transpose()

    def solve(self):
        set_printoptions(precision=5)
        set_printoptions(linewidth=150)
        # @type self truss
        self.calculateSupportedDof()


        for b in self.beams:
            self.addToGeneral(b)
    #    print "kGeneral"
    #    print kGeneral

        kff = zeros((self.freeDof,self.freeDof))
        ksf = zeros((self.supportedDof,self.freeDof))
        kfs = zeros((self.freeDof,self.supportedDof))
        kss = zeros((self.supportedDof,self.supportedDof))

    #    print self.dof

        ffj = 0
        sfj = 0
        fsj = 0
        ssj = 0
        sxi = 0
        fxi = 0

        for i in range(self.dofCount): #we take a column
            if self.dof[i]==1: #if this column is supported
                for j in range(self.dofCount): #for each item in the column
                    if self.dof[j]==1: #if the row is supported
                        kss[sxi,ssj]=self.kGeneral[i,j] #we fill kss
    #                    print "kss"
    #                    print kss
                        ssj += 1 #and go to next empty cell
                    else:
    #                    print "ksf"
    #                    print ksf
                        ksf[sxi,sfj]=self.kGeneral[i,j] #we fill ksf
                        sfj += 1 #and go to the next empty cell
                sxi +=1; #when an s row is finished we know
                    #that we filled the first row of both ksf and kss
                ssj = 0; sfj = 0 #and start over with the rows
            else:
                for j in range(self.dofCount):
                    if self.dof[j]:
                        kfs[fxi,fsj]=self.kGeneral[i,j]
                        fsj += 1
                    else:
                        kff[fxi,ffj]=self.kGeneral[i,j]
                        ffj += 1
                fxi += 1;
                fsj=0; ffj=0

    #    print "kff"
    #    print kff
    #    print "kss"
    #    print kss
    #    print "kfs"
    #    print kfs
    #    print "ksf"
    #    print ksf

    # build rf and us (vector of prescribed displacements)
        rf = zeros((self.freeDof))
        us = zeros((self.supportedDof))
        fi = 0; si = 0;
        for j in self.joints:
            if "x" in j.supports:
                us[si] = j.supports["x"]
                si += 1
            else:
                rf[fi]= j.getTotalLoadMagnitude().x; #total load magnitudes haven't been
                fi += 1                                     #initialized
            if "y" in j.supports:
                us[si] = j.supports["y"]
                si += 1
            else:
                rf[fi]= j.totalMagnitude.y;  #now the values of total magnitude are
                fi += 1                      #already stored in the variables so no need
                                             #to calculate again
    #make us and rf vertical vectors
        rf = array([rf]).transpose()
        us = array([us]).transpose()

#        print "rf | applied loads"
#        print rf
#        print "us | prescribed displacements"
#        print us

    #solve!
        uf = linalg.inv(kff).dot(rf-kfs.dot(us))
        rs = ksf.dot(uf)+kss.dot(us)

#        print "rs  | support reactions"
#        print rs

    #build u
        u = zeros((self.dofCount))
        fi = 0; i = 0;
        for j in self.joints:
            if "x" in j.supports:
                u[2*i] = j.supports["x"]
            else:
                u[2*i] = uf[fi]
                fi += 1
            if "y" in j.supports:
                u[2*i+1] = j.supports["y"]
            else:
                u[2*i+1] = uf[fi]
                fi += 1
            i += 1
#        print "u | displacements"
#        print u

    #store displacements in joints
        i = 0;
        for j in self.joints:
            if "x" in j.supports:
                j.displacement.x = u[2*i]
            if "y" in j.supports:
                j.displacement.y = u[2*i+1]

    #compute axial forces
        s = zeros((len(self.beams)))
        i = 0;
        for m in self.beams:
            s[i]=self.computeAxialForces(m, u)[0]
            #store axial forces in beams
            m.axial = s[i]
            i += 1

#        print "s | axial forces in beams"
#        print s


    

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
    axial = 0
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
        #βάζουμε τον πίνακα ktemp 4 φορές στον πίνακα klocal ως εξής
        # __________
        #|kte |-kt | --> klocal
        #|mp__|____|  /
        #|-kt | kt | /
        #|____|____|
        self.klocal = hstack((self.ktemp,-self.ktemp))
        self.klocal = vstack((self.klocal,-self.klocal))
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




if __name__ == "__main__":
    myTruss = truss(sys.argv[1])
    myTruss.solve()


#print myTruss.dof

#    for b in myTruss.beams:
#        print b.kglobal
#        print


#    for j in myTruss.joints:
#        print j

#    n1 = joint(0,0,0)
#    n2 = joint(1,0,1)
#
#    myBeam = beam(1, n1, n2)
#
#    print myBeam
