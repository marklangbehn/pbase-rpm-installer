#!/bin/bash

## working dir
cd /home/mark/work/virtualrecordlabel-site

##clean
rm -rf public
rm -rf .cache

## refresh and rebuild - creates "public" dir
git pull

yarn

gatsby build
