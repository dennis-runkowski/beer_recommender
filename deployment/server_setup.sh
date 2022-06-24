#!/bin/bash

echo "###############################"
echo "Ubuntu Cold Ones Server Install"
echo "###############################"


sudo getent group sudousers || sudo groupadd sudousers
sudo groupadd beer_recommender
sudo usermod -a -G beer_recommender www-data
sudo usermod -a -G sudousers beer_recommender

sudo chown beer_recommender:sudousers /opt
mkdir -p /opt/beer_recommender

echo "###############################"
echo "Adding core Linux repos"
echo "###############################"

sudo apt-get install software-properties-common
sudo apt-add-repository universe
sudo apt-get update

set -e

# Creating logging directories
sudo mkdir -p /var/log/flask_uwsgi
sudo chown -R www-data:www-data /var/log/flask_uwsgi


echo "###############################"
echo " Installing Python 3"
echo "###############################"

sudo apt-get update && sudo apt-get upgrade
sudo apt install python3

echo "alias python=python3" >> ~/.bashrc
echo "alias pip=pip3" >> ~/.bashrc

echo "###################################"
echo " Setup Virtualenv and Wrapper"
echo "###################################"

sudo apt install virtualenv
pip install virtualenvwrapper

echo ". /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
echo "WORKON_HOME=/opt/" >> ~/.bashrc

echo "###############################"
echo " Installing Nginx"
echo "###############################"

sudo apt-get install nginx

echo "###############################"
echo " Installing uWsgi"
echo "###############################"

sudo apt-get install uwsgi-emperor uwsgi
sudo apt-get install uwsgi-plugin-python


echo "##################################"
echo " Install Complete "
echo "##################################"

echo ""
echo "##################################"
echo " IMPORTANT "
echo "##################################"
echo "1. Install the virtual environment as follows:"
echo "$ source ~/.bashrc"
echo "$ mkvirtualenv virtualenv"
echo ""
echo "2. Create '/var/www/.filingsbot.ini' and populate accordingly"
echo ""
echo "3. Restart the emperor: systemctl restart emperor.uwsgi"
echo ""
echo "Some help commands below:"
echo ""
echo "workon virtualenv "
