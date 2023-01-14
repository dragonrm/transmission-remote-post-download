#!/usr/bin/python3.6
#####!/usr/bin/python3.6

import os
import time
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

def gettorrent():
##################### This function gets the torrent info and cuts it into two chunks - the ID and torrent name and
##################### returns it as a list. It's split on the spacing before the torrent name in the returned data from
##################### transmission.

        idle = sp.getoutput('transmission-remote sickchill:9091 -l | grep Idle')
        seeding = sp.getoutput('transmission-remote sickchill:9091 -l | grep Seeding')
        fin = sp.getoutput('transmission-remote sickchill:9091 -l | grep Finished')

        if idle != '':
                print("Result of idle ---- \n",idle)
                dataset = idle.split('\n')
                dataset.insert(0,"idle")
                result = dataset
        elif seeding !='':
                #print("Result of seeding ---- ",seeding)
                dataset = seeding.split('\n')
                dataset.insert(0,"seeding")
                result = dataset

        elif fin != '':
                #print("Result of finished ---- ",fin)
                dataset = fin.split('\n')
                dataset.insert(0,"fin")
                result = dataset

        else:
                print("Result of idle ---- ",idle)
                print("Result of seeding ---- ",seeding)
                print("Result of finished ---- ",fin)
                result = "No active torrents"

        return result



def cleantor(tors):
#        print("THIS IS THE TOR LIST SENT TO CLEAN -----------------", tors)
        i=1
        dataset = []
        while i < len(tors):
            if tors[0] == "idle":
               predataset = tors[i].split('         ')
               idreturn = predataset[0].split('   ')
               idreturn = idreturn[1].strip()
               dataset += [idreturn,predataset[-1]]
               i+=1
            elif tors[0] == "seeding":
               dataset = tors[i].split('      ')
               idreturn = predataset[0].split('   ')
               idreturn = idreturn[1].strip()
               dataset += [idreturn,predataset[-1]]

               i+=1
            elif tors[0] == "fin":
               dataset = fin.split('     ')
               idreturn = predataset[0].split('   ')
               idreturn = idreturn[1].strip()
               dataset += [idreturn,predataset[-1]]

               i+=1
            else:
               dataset = "NO DATA PREFIX"
               i+=1

        result = dataset
        return result




## Intialize out lists
torName=[]
torID=[]

#Get the torrent or torrents that are ready
tors = gettorrent()

#clean the torrents and grab just the ID and Name
output = cleantor(tors)


if tors == "No active torrents":
        print("There are no active torrents, exiting.......")
        quit()
print("THIS IS THE OUTPUT RETURNED LIST ----------------- \n",output)


#-------------------------------------
########################################################################
# now we have a clean directory and tor name. Some might have spaces so we need to make sure we
# quote the commands so they can pass correctly
time.sleep(2.5)


n = 2 # batch size
for i in range(0, len(output)-n+1, n):
    batch = output[i:i+n]
    print("BATCH DATA LIST ___________________________ ",batch,"\n\n -------------------------------")
    torName.append(batch[1].strip())
    torID.append(batch[0].strip())
    #print("TorID number ---- ",torID,"TorName ----- ",torName)

    #for i,f in enumerate(torName):
    for f in torName:
        print("This is the value we are running with *************************  ",f,"\n\n")
        regexp = re.compile(r'[sS]+[0-9]+[eE]')
        #this regex is used to see if the filename contains a Season number and Episode number
        #If the filename does then it's handled like a TV show and sent to the sickchill drop directory

        if regexp.search(f): #check for Season and Episode numbering
            showname=re.sub(r"^\s+","",f)
            print("This is a TV show. #################################################")
            # print("cp -a \"",fullpath,showname,"\" -t ",destpath,sep='')
            # print("\n\n")
            ## combine the path with the directory name
            source_dir=fullpath+showname
            tvpath=destpath+showname

            try:

                print("Copying directory for processing")
                print("THIS IS THE STUFF THATS COPYING ------ ",source_dir)
                distutils.dir_util.copy_tree(source_dir, tvpath)  #shutil.copytree(source_dir, destpath)
                print("Directory copy completed.\n________________________________________________________________")
            except:
                print("An exception occurred!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
                print >> sys.stderr, "Could not copy folder!!!!!!!!!!!!!!!!!!!!!!!!!!!"
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
                    #print("Walking through ", source_dir)
                    for f in the_files:
                        if f.lower().endswith(".rar"):
                            decompfile=source_dir+"/"+f
                            print("Found a rar file, gonna extract it. #######################\n ", f)
                            patoolib.extract_archive(decompfile,outdir=mvpath)
                            print("Extract files to -------------- ", mvpath)
                #distutils.dir_util.copy_tree(source_dir, moviepath)  #shutil.copytree(source_dir, destpath)

            except:
                print("An exception occurred")
                print >> sys.stderr, "Could not copy folder!!!!!!!!!!!!!!!!!!!!!!!\n"
                print >> sys.stderr, "Exception: %s" % str(e)
                exit(1)
            try:
                print("\nThere were no compressed files so let see if it's just a single file movie.\n")
                #print("This is the name we are working with ----------------------------",filname)
                for root,_,the_files in os.walk(source_dir):
                    print("Looking for video files in - ",root," we have found - ",the_files)

                    for name in the_files:
                        #print("This is the NAME in this loop ------------------ ",name)
                        if name.lower().endswith(".mkv") or name.lower().endswith(".mp4") or name.lower().endswith(".avi"):
                           if "sample" in name.lower():
                              print("\n\nThis is a sample file and we will NOT copy this ------- ",name)
                              continue

                           filname=showname.split('      ')
                           source_dir=fullpath+filname[-1]
                           movie_dir=root+"/"+name
                           #print("Found the file-------------- ",name)
                           print("Copying file over to the movie server ---- ",movie_dir)
                           copycmd="distutils.file_util.copy_file(%s,%s)"%(movie_dir,mvpath)
                           print(copycmd)
                           try:
                               distutils.file_util.copy_file(movie_dir,mvpath)
                               print("Movie has been transfered to the movie directory")

                           except:
                               print("An exception occurred")
                               print >> sys.stderr, "file copy of movie failed"
                               print >> sys.stderr, "Exception: %s" % str(e)
                               exit(1)


        #            else:
        #                print("No single file movie found, must be in a sub directory.")
        #                print("THIS IS THE PATH AND FILE ----- ",filname[-1])
        #                source_dir=fullpath+filname[-1]
        #                distutils.dir_util.copy_tree(source_dir, mvpath)

            except:
                print("An exception occurred")
                print >> sys.stderr, "Could not copy file!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                print >> sys.stderr, "Exception: %s" % str(e)
                exit(1)


        #print("\nNow we can remove the torrents with the ID ----- ",torID[i],"\n\n")
        #print("transmission-remote sickchill:9091 -t ",torID[i]," -rad",sep='')



    removetor="transmission-remote sickchill:9091 -t %s -rad"%(torID[0])
    print(removetor)
    torName.clear()
    torID.clear()
    try:
        os.system(removetor)
        print("This would remove the torrent\n\n\n")
    except:
        print("An exception occurred")
        print >> sys.stderr, "does not exist"
        print >> sys.stderr, "Exception: %s" % str(e)
        exit(1)






#----------------------------------------






