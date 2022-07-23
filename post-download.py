#!/usr/bin/python

import os
import re
import shutil
import subprocess as sp 
import distutils.core
#############################
#
#   Setup some folder info for later
#   There are different paths for TV and Movies
#   

#############################

#   ************ Change the paths below to match your needs *****************
destpath="/home/downloads/.process/"
mvpath="/home/downloads/"
fullpath="/torrent-nzb/torrents/"

## Intialize out lists
torName=[]
torID=[]

#### ---- Get the output from the transmission server for tors that are at Idle
output = sp.getoutput('transmission-remote sickchill:9091 -l | grep Idle')

#### ----- Split the single return in to a list
output = output.split('\n')

######### Here's the less than stellar output we need to deal with from transmission-remote
#   ID   Done       Have  ETA           Up    Down  Ratio  Status       Name
#     1   100%   540.9 MB  Done         0.0     0.0    0.0  Idle         TORRENT NAME MIGHT HAVE Spaces
#     2   100%   193.6 MB  Done         0.0     0.0    0.0  Idle         Torrent.name.might.not.have.spaces
#Sum:            734.5 MB               0.0     0.0
######### Since we at least grep for only the Idle status we don't need to worry about the tope and bottom rows
###### So as you can see above the largest space blocks are 9 wide.


#### ------ Now to carve out what we need from each list item
for i in output:
    
    # we need to cut on the largest space block which should be the space between the Idle state and the Name
    carve1= i.split('         ')
    #print(carve1)
    ## we only need to keep item 2 from the carved up list item and append it to the new list
    torName.append(carve1[-1].strip())

    ## Lets get the ID for each torrent so we can remove it after our copy
    carve2= i.split('   ')
    #print(carve2[1])
    torID.append(carve2[0].strip())


########################################################################
# now we have a clean directory and tor name. Some might have spaces so we need to make sure we
# quote the commands so they can pass correctly

for i,f in enumerate(torName):

    regexp = re.compile(r'[sS]+[0-9]+[eE]')

    if regexp.search(f):
        showname=re.sub(r"^\s+","",f)
        #print("cp -a \"",fullpath,showname,"\" -t ",destpath,sep='')
        ## combine the path with the directory name
        source_dir=fullpath+showname
        tvpath=destpath+showname
        
        try:
            distutils.dir_util.copy_tree(source_dir, tvpath)  #shutil.copytree(source_dir, destpath)
        except:
            print("An exception occurred")
            print >> sys.stderr, "Could not copy folder"
            print >> sys.stderr, "Exception: %s" % str(e)
            sys.exit(1)
        

    else:
        showname=re.sub(r"^\s+","",f)
        #print("cp -a \"",fullpath,showname,"\" -t ",destpath,sep='')
        ## combine the path with the directory name
        source_dir=fullpath+showname
        moviepath=mvpath+showname
        
        try:
            distutils.dir_util.copy_tree(source_dir, moviepath)  #shutil.copytree(source_dir, destpath)

        except:
            print("An exception occurred") 
            print >> sys.stderr, "Could not copy folder"
            print >> sys.stderr, "Exception: %s" % str(e)
            sys.exit(1)

    removetor="transmission-remote sickchill:9091 -t %s -rad"%(torID[i])

    try:
        os.system(removetor)
    except:
        print("An exception occurred")
        print >> sys.stderr, "does not exist"
        print >> sys.stderr, "Exception: %s" % str(e)
        sys.exit(1)

