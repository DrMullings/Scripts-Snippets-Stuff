#!/bin/bash

#TODO
# Write Parser for long arguments
# LONGARGS: ID [id], O3|OSD|[URL],
# get URL by regex
# get ID by relative position to URL?
# implement more Flags and Parameters as wrap-up, e.g. RAM for QEMURAM

# Variables:
ME="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
CJ='/usr/share/openqa/script/clone_job.pl '
JOBID='0'
FIRSTARGS=''
LASTARGS=''
RUN='1'
SOURCE=''

# Functions:

help() {
    echo -e "Usage: "
    echo -e "$ME -j ID -s [O3|OSD|<URL>] "
    echo -e "\t ID = Job ID to be cloned"
    echo -e "\t -o [OPTIONS] \t\t options passed to openqa"
    echo -e "\t -p [PARAMETERS] \t parameters for clone_job"
    echo -e "\t -n [int] \t\t clone ID int times"
    #TODO
    exit
}

# Parse parameters
while getopts 'j:n:o:s:n:p:' OPTION;
do
    case $OPTION in
        j) JOBID=$OPTARG;;
        n) RUN=$OPTARG;;
        o) LASTARGS=$OPTARG;;
        s) SOURCE=$OPTARG;;
        n) RUN=$OPTARG;;
        p) FIRSTARGS=$OPTARG;;
        *) help;;
    esac
done

# Check source parameter
if [ $SOURCE == "O3" ] 
then
    SOURCE='https://openqa.opensuse.org'
    elif [ $SOURCE == "OSD"  ] 
    then 
        SOURCE='https://openqa.suse.de'
fi



# Run clone_job

for ((i=0;i< $RUN;i+=1))
do
    #echo "$CJ $FIRSTARGS --from $SOURCE $JOBID $LASTARGS"
    $($CJ $FIRSTARGS --from $SOURCE $JOBID $LASTARGS)
done
