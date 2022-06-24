#!/bin/bash
set -e

timestamp=$(date +%s)
echo "###############################"
echo " Backing up /opt/cold_ones"
echo "###############################"

# Backup code
mkdir -p /home/coldones/backups
tar -zcvf /home/coldones/backups/backup_$timestamp.tar.gz /opt/cold_ones

# Clean up old backups
find /home/coldones/backup* -mtime +15 -exec rm {} \;

echo "###############################"
echo " Installing cold_ones...."
echo "###############################"

package_name=$(ls /tmp/package/build* -Art | tail -n 1)
cd /tmp/package && tar -zxvf $package_name
cd /tmp/package && rsync -r cold_ones/* /opt/cold_ones/
sudo rm -rf /tmp/package

# Ensure permissions
sudo chown -R coldones:coldones /opt/cold_ones/

echo "###############################"
echo " Installing Python Packages"
echo "###############################"

# source virtualenv
source /opt/virtualenv/bin/activate

cd /opt/cold_ones
pip install -r requirements.txt
python setup.py develop
cd /opt/cold_ones/deployment

# Ensure permissions again for safety
sudo chown -R coldones:coldones /opt/cold_ones/

echo "###################################"
echo " Setting up uwsgi and nginx config"
echo "###################################"

# uwsgi config
sudo mv /opt/cold_ones/deployment/uwsgi_emperor/emperor.uwsgi.service /etc/systemd/system/
sudo mv /opt/cold_ones/deployment/uwsgi_vassals/wsgi_website.ini /etc/uwsgi-emperor/vassals/

# nginx
sudo mv /opt/cold_ones/deployment/nginx/cold_ones /etc/nginx/sites-available/
set +e
sudo ln -s /etc/nginx/sites-available/cold_ones /etc/nginx/sites-enabled
set -e
echo "###################################"
echo " Restarting nginx and uwsgi emperor"
echo "###################################"

sudo systemctl daemon-reload
sudo systemctl enable nginx emperor.uwsgi
sudo systemctl restart nginx
sudo systemctl restart emperor.uwsgi

echo "###################################"
echo " Completed!"
echo "###################################"
echo ""
# systemctl stop uwsgi-emperor
# systemctl disable uwsgi-emperor