#!/bin/bash

## copy in pre-reqs
cd /var/www/html/pbase-foundation/public
cp -r .abba /home/mark/work/pbase-foundation-site/public
cp .htaccess /home/mark/work/pbase-foundation-site/public

## deploy
cd /var/www/html/pbase-foundation/
mv public public-$(date +"%Y-%m-%d_%H-%M-%S")
mv /home/mark/work/pbase-foundation-site/public .

## links to media
cd /var/www/html/pbase-foundation/public
ln -s /var/www/mp3 mp3
