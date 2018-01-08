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

#TODO get sudo without passwd
echo "Setting sudo"
sudo echo "$USER ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER

echo "Setting path"
echo "sudo export PATH=$PATH:/home/$USER/Scripts" >> /etc/bash.bashrc.local

echo "Setting vimrc"
sudo cp $(pwd)/vimrc /etc/vimrc
