#!/bin/bash

## copy in pre-reqs
cd /var/www/html/pbase-foundation.com/public
cp -r .abba /home/mark/work/pbase-foundation-site/public
cp .htaccess /home/mark/work/pbase-foundation-site/public

## deploy
cd /var/www/html/pbase-foundation.com/
mv public public-$(date +"%Y-%m-%d_%H-%M-%S")
mv /home/mark/work/pbase-foundation-site/public .

## links to media
cd /var/www/html/pbase-foundation.com/public
ln -s /var/www/mp3 mp3
#ln -s /var/www/wav wav

## yum
ln -s /var/www/yum-repo yum-repo
ln -s /var/www/yum-repo/pbase-components/1.0/RPMS/pbase-preconfig-1.0-0.noarch.rpm pbase-preconfig.rpm
