import array
from numpy import *

d =  array([[1.,2.,3.],
           [4.,5.,6.]])
#a = a[[3,3,3]]
a = zeros((1,3))
a = append(a, [d[1]], axis=0)
#a[1,:] = zeros((1,3))
#a[2]= [0,0,0]

#print array([d[:][:,2]]).transpose()
#
#a = zeros((4,2))
#
#a[2,1]=1
#print a

d = {'key':'value', 'ke2' : 'v3'}

for i in d:
    print d[i]