ItemCatalog-fullstack-nanodegree-project3
=============
# Description
Build an item catalog. Each item belongs to a catalog. User can brower all items and catalog.
A user can log in the web by Google or FB or registered as a customer in our web.
A registered user can brower all items and they can modify/delete the catalogs/ items they created. But they cant modify/delete catalog/item doesn't belong to them.

develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

Modern web applications perform a variety of functions and provide amazing features and utilities to their users; but deep down, it’s really all just creating, reading, updating and deleting data. In this project, you’ll combine your knowledge of building dynamic websites with persistent data storage to create a web application that provides a compelling service to your users.

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
1. Build database: python2 database_setup.py
2. Insert data into database: python2 initdatabase.py
## Init web
1. python2 webserver.py
## Init redis server
1. open another vagrant machine.
2. open another terminal.
3. cd vagrant
4. vagrant up
5. vagrant ssh
6. cd catalog
7. redis-server
## Visit web
1. visit in your brower. localhost:8000

## Test Instructions
1. To log in. click 'log in' in the nav bar. You can log in as: username: user1 user2 user3.... the corresponding password is password1 password2.... Or log in as a new user. If your user name is not used before, you will default to sign up by log in. You can also log in as google or fb user by clicking button in log in page.
2. After logged in, you should jump to home page. To log off click top 'log off' and able to add new catalog by 'create new catalog'. In catalog, you will be able to add item. If the catalog is created by userA, only userA will be able to modify the catalog. But all logged in users are able to add items in each catalog. But If an item is created by some one, others can't modify that item.
3. If you are logged off, you can see all catalogs and items but you dont have access to modify/ delete them.
4. JSON end point. format: localhost:8000/home/<string:owner_name>/<string:item_name>/JSON owner_name is the catalog name, and item_name is the item name under that catalog. Ex. http://localhost:8000/home/dance/Africa/JSON

## Default DataBase
### User Password
1. user1  password1
2. user2  password2
3. user3  password3
4. user4  password4
5. user5  password5
#### Catalog
1. literature
2. sculpture
3. drawing
4. dance
5. theatre
6. painting
#### Items 
Relations and items pls see initdatabase.py
    
