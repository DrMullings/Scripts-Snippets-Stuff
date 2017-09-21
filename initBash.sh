#!/bin/bash
USER=$(whoami)

# set alias
echo "Setting aliases"
ALIASFILE="/home/$USER/.alias"

echo 'alias l="ls "' >> $ALIASFILE
echo 'alias ll="ls -l "' >> $ALIASFILE
echo 'alias la="ls -a "' >> $ALIASFILE
echo 'alias lla="ls -la "' >> $ALIASFILE
echo 'alias sudo="sudo "' >> $ALIASFILE

echo "Setting path"
echo "export PATH=$PATH:/home/$USER/Scripts" >> /etc/bash.bashrc.local
