# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="qwazix"
__date__ ="$Jan 25, 2013 1:37:23 PM$"

if __name__ == "__main__":
    print "Hello World"


#    build kfg (fill in the rows of free degrees, leaving all the columns
#    intact as in the kgen
    freei = 0
    kfg = zeros((1,2*len(myTruss.joints)))
    for joint in myTruss.joints:
        # @type joint joint
        if not "x" in joint.supports :
            kfg = append(kfg, [kGeneral[2*joint.id]], axis=0)
            freei = freei + 1
        if not "y" in joint.supports :
            kfg = append(kfg, [kGeneral[2*joint.id+1]], axis=0)
            freei = freei + 1
    print "kfg"
    print kfg
#build kff (fill in the columns of free degrees of the kfg)
    kff = zeros((2*len(myTruss.joints)-myTruss.supportedDof,2*len(myTruss.joints)-myTruss.supportedDof))
    print getColumn(kfg,2*joint.id)
    for joint in myTruss.joints:
        # @type joint joint
        if not "x" in joint.supports :
            kff = hstack((kff, getColumn(kfg,2*joint.id)))
            freei = freei + 1
        if not "y" in joint.supports :
            kff = hstack((kff, getColumn(kfg,2*joint.id+1)))
            freei = freei + 1
    print "kff"
    print kff
#build kfs
    kfs = zeros((2*len(myTruss.joints),1))
    for joint in myTruss.joints:
        # @type joint joint
        if "x" in joint.supports :
            kfs = hstack((kfs, getColumn(kfg,2*joint.id)))
            freei = freei + 1
        if "y" in joint.supports :
            kfs = hstack((kfs, getColumn(kfg,2*joint.id+1)))
            freei = freei + 1
    print "kfs"
    print kfs

#build ksg (fill in the rows of supported dof's, leaving all the columns of
#the general kgen intact)
    ksg = zeros((2*len(myTruss.joints),1))
    print
    for joint in myTruss.joints:
        # @type joint joint
        if not "x" in joint.supports :
            ksg = vstack((ksg, kGeneral[2*joint.id]))
            freei = freei + 1
        if not "y" in joint.supports :
            ksg = vstack((ksg, kGeneral[2*joint.id+1]))
            freei = freei + 1
    print "ksg"
    print ksg
