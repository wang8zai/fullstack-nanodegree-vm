ItemCatalog-fullstack-nanodegree-project3
=============
# Prerequisite
## python2.7
pakage: Flask, Sqlalchemy
## Vagrant Redis

# Installtion
## intall vagrant machine
Download: https://www.vagrantup.com/downloads.html
## install sqlalchemy
Download: https://www.sqlalchemy.org/download.html
## install flask
Download: https://pypi.org/project/Flask/1.0.2/
## clone project
git clone https://github.com/wang8zai/fullstack-nanodegree-vm

# Run
## Directionary
cd vagrant
## Run virtual machine
vagrant up
vagrant ssh
cd /vagrant
## Directionary
cd catalog
## Init database
Build database:
python2 database_setup.py
Insert data into database:
python2 initdatabase.py
## Init web
python2 webserver.py
## Init redis server
open another vagrant machine:
open another terminal.
cd vagrant
vagrant up
vagrant ssh
cd catalog
redis-server
## Visit web
visit in your brower.
localhost:8000


