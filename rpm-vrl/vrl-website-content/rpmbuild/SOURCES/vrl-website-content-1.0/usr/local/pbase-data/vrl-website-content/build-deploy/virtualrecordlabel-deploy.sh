#!/bin/bash

## copy in pre-reqs
cd /var/www/virtualrecordlabel.net/public
cp -r .abba /home/mark/work/virtualrecordlabel-site/public
cp .htaccess /home/mark/work/virtualrecordlabel-site/public

## deploy
cd /var/www/virtualrecordlabel.net/
mv public public-$(date +"%Y-%m-%d_%H-%M-%S")
mv /home/mark/work/virtualrecordlabel-site/public .

## links to media
cd /var/www/virtualrecordlabel.net/public
ln -s /var/www/mp3 mp3
#ln -s /var/www/wav wav

## yum
#ln -s /var/www/yum-repo yum-repo
#ln -s /var/www/yum-repo/pbase-components/1.0/RPMS/pbase-preconfig-1.0-3.noarch.rpm pbase-repo.rpm
#ln -s /var/www/yum-static/ yum-static
