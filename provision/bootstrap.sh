#!/bin/bash

# set the session to be noninteractive
export DEBIAN_FRONTEND="noninteractive"

# update apt-get
apt-get update
apt-get upgrade

apt-get -q -y install build-essential daemon

# install basics
apt-get -q -y install python-dev python-pip libpq-dev python-gi libxml2-dev libxslt-dev libffi-dev libssl-dev

# Install postgres
echo "INFO: Installing postgresql..."
# install
echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" > /etc/apt/sources.list.d/postgres.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt-get update
apt-get install -y postgresql-9.5 postgresql-client-9.5 postgresql-contrib-9.5 2>&1

# configure Postgres
# INSECURE!!!
cp /vagrant/psql/postgresql.conf /etc/postgresql/9.5/main/postgresql.conf
cp /vagrant/psql/pg_hba.conf /etc/postgresql/9.5/main/pg_hba.conf
service postgresql restart

# rebuild the database
echo "INFO: Setting up the database..."
# INSECURE!!!
su - postgres -c "psql -c \"ALTER USER postgres with encrypted password 'postgres';\""
su - postgres -c "psql -f /vagrant/psql/db_reset.sql"
service postgresql restart


## Install nginx
echo "INFO: Installing nginx..."

# add the nginx apt-get repo
echo "deb http://nginx.org/packages/ubuntu/ trusty nginx" > /etc/apt/sources.list.d/nginx.list
wget -q -O - http://nginx.org/keys/nginx_signing.key | apt-key add -
apt-get update

# install
apt-get -q install -y nginx=1.10.0*
service nginx restart

# setup logs folder
mkdir -p /var/log/nginx/
chown -R www-data:www-data /var/log/nginx/

# copy over configs, restart
# INSECURE!!!
cp -R /vagrant/nginx/* /etc/nginx/
mkdir -p /etc/nginx/sites-enabled/
rm /etc/nginx/conf.d/default.conf
service nginx restart 2>&1


# install requirements
pip install -r /vagrant/pip_requirements.txt 2>&1

## Install uWSGI
echo "INFO: Installing uWSGI..."

# install
apt-get -q install -y uwsgi uwsgi-plugin-python
service uwsgi restart 2>&1

# init logs
mkdir -p /var/log/infosec_mentor_project/
touch /var/log/infosec_mentor_project/info.log
chown -R www-data:www-data /var/log/infosec_mentor_project
chmod 0777 /var/log/infosec_mentor_project/info.log # INSECURE!!!

# config www-data user shell
chsh -s /bin/bash www-data

# copy over configs, restart
cp /vagrant/uwsgi/* /etc/uwsgi/apps-enabled/
service uwsgi restart 2>&1

# Initialize the database via the pyton manage script
python /var/www/infosec_mentor_project/manage.py initdb

updatedb;
exit;