#!/bin/bash

## deploy
cd /var/www/html/pbase-foundation.com/
mv public public-$(date +"%Y-%m-%d_%H-%M-%S")
mv /root/work/pbase-foundation-site/public .


echo "Copying .abba/ and .htaccess resources"
cd /usr/local/pbase-data/pbase-website-content/build-deploy/resources/

tar xf DOT.abba.tar -C /var/www/html/pbase-foundation.com/public/
/bin/cp --no-clobber DOT.htaccess /var/www/html/pbase-foundation.com/public/.htaccess


## links to media
cd /var/www/html/pbase-foundation.com/public
ln -s /var/www/mp3 mp3
#ln -s /var/www/wav wav

## yum
#ln -s /var/www/yum-repo yum-repo
#ln -s /var/www/yum-repo/pbase-components/1.0/RPMS/pbase-repo-1.0-3.noarch.rpm pbase-repo.rpm
#ln -s /var/www/yum-repo/pbase-components/1.0/RPMS/pbase-repo-next-1.0-3.noarch.rpm pbase-repo-next.rpm
#ln -s /var/www/yum-static/ yum-static
