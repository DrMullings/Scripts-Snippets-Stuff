#!/bin/bash
#TODO set user permissions for openqa
# /var/lib/openqa

# check privileges
if [ "$(whoami)" != "root" ]
then
    echo "Root privileges required"
    exit
fi

echo "Installing openQA"

zypper ar -f obs://devel:openQA/openSUSE_Leap_42.3 openQA
zypper ar -f obs://devel:openQA:Leap:42.2/openSUSE_Leap_42.3 openQA-perl-modules

zypper in openQA

echo "Configuring Apache"

a2enmod headers
a2enmod proxy
a2enmod proxy_http
a2enmod proxy_wstunnel

cp /etc/apache2/vhosts.d/openqa.conf.template /etc/apache2/vhosts.d/openqa.conf

echo "Configuring openqa.ini"

OQAINI="/etc/openqa/openqa.ini"

#Backup default ini

if [ -e $OQAINI  ]
then
    mv $OQAINI $(OQAINI).bak
fi

echo "[global]" >> $OQAINI
echo "[auth]" >> $OQAINI
echo "method = Fake" >> $OQAINI
echo "[logging]" >> $OQAINI
echo "[openid]" >> $OQAINI
echo "httpsonly = 0" >> $OQAINI
echo "[audit]" >> $OQAINI
echo "blacklist = job_grab job_done" >> $OQAINI
echo "[amqp]" >> $OQAINI

echo "Enabling and starting services"

systemctl start openqa-scheduler
systemctl start openqa-gru
systemctl start openqa-websockets
systemctl start openqa-webui

systemctl restart apache2

systemctl enable openqa-scheduler
systemctl enable openqa-gru
systemctl enable openqa-websockets
systemctl enable openqa-webui

echo "Installing workers"

zypper in openQA-worker

WORKERINI="/etc/openqa/client.conf"
KEY="1234567890ABCDEF"
SECRET=$KEY

/usr/share/openqa/script/create_admin --key=$KEY --secret=$SECRET

echo "[localhost]" >> $WORKERINI
echo "key = $KEY" >> $WORKERINI
echo "secret = $SECRET" >> $WORKERINI

