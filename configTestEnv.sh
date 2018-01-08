#!/bin/bash
USER=$(whomai)

echo 'Initializing directories'
GITPATH=/home/$USER/Git
mkdir -p $GITPATH
DISTRIOS=$GITPATH/os-autoinst-distri-opensuse/
OQAPATH=$GITPATH/openQA

cd $GITPATH

echo 'Cloning tests'
git clone git@github.com:os-autoinst/os-autoinst-distri-opensuse.git
git clone git@github.com:os-autoinst/os-autoinst-distri-openQA.git

echo 'Cloning needles for SLES'
echo 'please clone SLES needles yourself, since not public available'

echo 'Cloning needles for opensuse'
cd $DISTRIOS/products/opensuse
git clone git@github.com:os-autoinst/os-autoinst-needles-opensuse.git needles

TESTPATH="/var/lib/openqa/share/tests"
FSPARAMS="none defaults,bind 0 0
"
echo 'Configuring mounts '
sudo echo "$DISTRIOS $TESTPATH/sle $FSPARAMS" >> /etc/fstab
sudo echo "$DISTRIOS $TESTPATH/opensuse $FSPARAMS" >> /etc/fstab
sudo echo "$OQAPATH $TESTPATH/openqa $FSPARAMS" >> /etc/fstab
