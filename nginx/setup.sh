#!/bin/bash

#Setting up NGINX required files for SSL support

echo Copying ssl files to current directory...;

sudo cp -r /etc/ssl ./ssl;

echo Changing MODE so docker can COPY;

sudo chmod 777 ssl -R;

