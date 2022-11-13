#!/usr/bin/python3.6
#####!/usr/bin/python3.6

import os
import sys
import re
import time
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

def gettorrent():
##################### This function gets the torrent info and cuts it into two chunks - the ID and torrent name and
##################### returns it as a list. It's split on the spacing before the torrent name in the returned data from
##################### transmission.

        idle = sp.getoutput('transmission-remote sickchill:9091 -l | grep Idle')
        seeding = sp.getoutput('transmission-remote sickchill:9091 -l | grep Seeding')
        fin = sp.getoutput('transmission-remote sickchill:9091 -l | grep Finished')

        if idle != '':
                print("Result of idle ---- ",idle)
                dataset = idle.split('         ')
                idreturn = dataset[0].split('   ')
                idreturn = idreturn[1].strip()
                print("This is the return data from transmission ------ ",dataset)
                result = [idreturn,dataset[-1]]
        elif seeding !='':
                print("Result of seeding ---- ",seeding)
                dataset = seeding.split('      ')
                idreturn = dataset[0].split('   ')
                idreturn = idreturn[1].strip()
                print("This is the return data from transmission ------ ",dataset)
                result = [idreturn,dataset[-1]]
        elif fin != '':
                print("Result of finished ---- ",fin)
                dataset = fin.split('     ')
                idreturn = dataset[0].split('   ')
                idreturn = idreturn[1].strip()
                print("This is the return data from transmission ------ ",dataset)
                result = [idreturn,dataset[-1]]
        else:
                print("Result of idle ---- ",idle)
                print("Result of seeding ---- ",seeding)
                print("Result of seeding ---- ",fin)
                result = "No active torrents"

        return result



## Intialize out lists
torName=[]
torID=[]


output = gettorrent()
if output == "No active torrents":
        print("There are no active torrents, exiting.......")
        quit()
print("THIS IS THE OUTPUT RETURNED LIST ----------------- ",output)

torName.append(output[-1].strip())

print("TorID number ---- ",output[0])
torID.append(output[0].strip())

########################################################################
# now we have a clean directory and tor name. Some might have spaces so we need to make sure we
# quote the commands so they can pass correctly
time.sleep(2.5)

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
            if showname.lower().endswith(".mkv") or showname.lower().endswith(".mp4") or showname.lower().endswith(".avi"):
                filname=showname.split('      ')
                source_dir=fullpath+filname[-1]
                print("Copying file over to the movie server ---- ",source_dir)
                distutils.file_util.copy_file(source_dir,mvpath)
            else:
                print("No single file movie found, must be in a sub directory.")
                print("THIS IS THE PATH AND FILE ----- ",filname[-1])
                source_dir=fullpath+filname[-1]
                distutils.dir_util.copy_tree(source_dir, mvpath)

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
