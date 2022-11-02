#!/usr/bin/python3.6
#####!/usr/bin/python3.6

import os
import sys
import re
import shutil
import subprocess as sp
import distutils.core
import patoolib
import pyunpack
#############################
#
#   Setup some folder info for later
#   There are different paths for TV and Movies
#
#############################
destpath="/home/downloads/.process/"
mvpath="/home/movies/movies/"
fullpath="/torrent-nzb/torrents/"
#################################




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
    #carve1=["The.Forgiven.2021.720p.WEB.H264-KBOX"]
    print(carve1)
    ## we only need to keep item 2 from the carved up list item and append it to the new list
    torName.append(carve1[-1].strip())

    ## Lets get the ID for each torrent so we can remove it after our copy
    carve2= i.split()
    #carve2=["12"]
    print("TorID number ---- ",carve2[0])
    torID.append(carve2[0].strip())

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


########################################################################
# now we have a clean directory and tor name. Some might have spaces so we need to make sure we
# quote the commands so they can pass correctly

for i,f in enumerate(torName):

    regexp = re.compile(r'[sS]+[0-9]+[eE]')
    #this regex is used to see if the filename contains a Season number and Episode number
    #If the filename does then it's handled like a TV show and sent to the sickchill drop directory

    if regexp.search(f): #check for Season and Episode numbering
        showname=re.sub(r"^\s+","",f)
        print("This is a TV show.          ")
        #print("cp -a \"",fullpath,showname,"\" -t ",destpath,sep='')
        ## combine the path with the directory name
        source_dir=fullpath+showname
        tvpath=destpath+showname

        try:

            print("Moving directory for processing")
            print("THIS IS THE STUFF THATS MOVING ------ ",source_dir)
            distutils.dir_util.copy_tree(source_dir, tvpath)  #shutil.copytree(source_dir, destpath)
            print("Directory move completed.")
        except:
            print("An exception occurred")
            print >> sys.stderr, "Could not copy folder"
            print >> sys.stderr, "Exception: %s" % str(e)
            exit(1)


    else: #Season and Episode info not found so it's not a TV show, we can send it to the movie directory
        showname=re.sub(r"^\s+","",f)
        filname=showname.split('      ')
        #print("cp -a \"",fullpath,showname,"\" -t ",destpath,sep='')
        ## combine the path with the directory name
        source_dir=fullpath+showname
        moviepath=mvpath+showname
        #print("THIS SHOULD BE THE SHOW NAME ------ ",filname[-1])

        try:
            print("This is most likely a movie, let's see if there's any compressed files here")
            for root,_,the_files in os.walk(source_dir):
                print("Walking through ", source_dir)
                for f in the_files:
                    if f.lower().endswith(".rar"):
                        decompfile=source_dir+"/"+f
                        print("Found a rar file, gonna extract it.  ", f)
                        patoolib.extract_archive(decompfile,outdir=mvpath)

            #distutils.dir_util.copy_tree(source_dir, moviepath)  #shutil.copytree(source_dir, destpath)

        except:
            print("An exception occurred")
            print >> sys.stderr, "Could not copy folder"
            print >> sys.stderr, "Exception: %s" % str(e)
            exit(1)
        try:
            print("There were no compressed files so let see if it's just a single file movie.")
            if f.lower().endswith(".mkv") or f.lower().endswith(".mp4") or f.lower().endswith(".avi"):
                filname=showname.split('      ')
                source_dir=fullpath+filname[-1]
                print("Copying file over to the movie server ---- ",source_dir)
                distutils.file_util.copy_file(source_dir,mvpath)

        except:
            print("An exception occurred")
            print >> sys.stderr, "Could not copy file"
            print >> sys.stderr, "Exception: %s" % str(e)
            exit(1)


    #print("\nNow we can remove the torrents with the ID ----- ",torID[i],"\n\n")
    #print("transmission-remote sickchill:9091 -t ",torID[i]," -rad",sep='')



    removetor="transmission-remote sickchill:9091 -t %s -rad"%(torID[i])
    print(removetor)
    try:
        os.system(removetor)
        #print("This would remove the torrent")
    except:
        print("An exception occurred")
        print >> sys.stderr, "does not exist"
        print >> sys.stderr, "Exception: %s" % str(e)
        exit(1)
