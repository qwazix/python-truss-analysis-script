#import array
#from numpy import *
#
#d =  array([[1.,2.,3.],
#           [4.,5.,6.]])
##a = a[[3,3,3]]
#a = zeros((1,3))
#a = append(a, [d[1]], axis=0)
##a[1,:] = zeros((1,3))
##a[2]= [0,0,0]
#
##print array([d[:][:,2]]).transpose()
##
##a = zeros((4,2))
##
##a[2,1]=1
##print a
#
#d = {'key':'value', 'ke2' : 'v3'}
#
#for i in d:
#    print d[i]

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def update_line(num, data, line):
    line.set_data(data[...,:num])
    return line,

fig1 = plt.figure()

data = np.random.rand(2, 25)
l, = plt.plot([], [], 'r-')
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.xlabel('x')
plt.title('test')
line_ani = animation.FuncAnimation(fig1, update_line, 25, fargs=(data, l),
    interval=50, blit=True)
#line_ani.save('lines.mp4')

fig2 = plt.figure()

x = np.arange(-9, 10)
y = np.arange(-9, 10).reshape(-1, 1)
base = np.hypot(x, y)
ims = []
for add in np.arange(15):
    ims.append((plt.pcolor(x, y, base + add, norm=plt.Normalize(0, 30)),))

im_ani = animation.ArtistAnimation(fig2, ims, interval=50, repeat_delay=3000,
    blit=True)
#im_ani.save('im.mp4', metadata={'artist':'Guido'})

plt.show()