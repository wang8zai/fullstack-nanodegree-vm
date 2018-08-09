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
1. cd vagrant
## Run virtual machine
1. vagrant up
2. vagrant ssh
3. cd /vagrant
## Directionary
1.  cd catalog
## Init database
1.Build database:
2. python2 database_setup.py
3. Insert data into database:
4. python2 initdatabase.py
## Init web
1. python2 webserver.py
## Init redis server
1. open another vagrant machine:
2. open another terminal.
3. cd vagrant
4. vagrant up
5. vagrant ssh
6. cd catalog
7. redis-server
## Visit web
1. visit in your brower. localhost:8000


