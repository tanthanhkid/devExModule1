#!/bin/sh
# Use this to install software packages
sudo yum update -y
sudo yum -y install httpd php
sudo chkconfig httpd on
sudo service httpd start

