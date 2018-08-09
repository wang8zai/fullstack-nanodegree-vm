from flask import Flask, render_template, request,\
                  redirect, jsonify, url_for, flash, g, make_response
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Owner, User, Item
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets,\
                                FlowExchangeError
import ratelimit
import httplib2
import json
import random
import string
import requests

auth = HTTPBasicAuth()

app = Flask(__name__)

# check same thread set to false.
engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False},)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"


# flask decorator to verify password.
@auth.verify_password
def verify_password(username_or_token, password):
    # Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(name=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# home page of the web.
# Display top 10 new added item.
# html rendered by serveral inputs
@app.route('/')
@app.route('/home')
def home():
    owners = session.query(Owner).all()
    items = session.query(Item)\
                   .order_by(desc(Item.created_date)).limit(10).all()
    status = request.args.get('status')
    if 'username' not in login_session:
        return render_template('home.html', owners=owners,
                               items=items, logged=False, status=status)
    else:
        return render_template('home.html', owners=owners,
                               items=items, logged=True, status=status)


# login page.
# Use a token to auth.
# login session records user info.
@app.route('/home/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        status = request.args.get('status', '')
        login_session['state'] = state
        return render_template('login.html', STATE=state, status=status)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if session.query(User).filter_by(name=username).first() is None:
            user = User(name=username)
            user.hash_password(password)
            session.add(user)
            session.commit()
        user = session.query(User)\
                      .filter_by(name=username).first()
        if not user.verify_password(password):
            return redirect(url_for('login', status='fail'))
        login_session['provider'] = 'itemcatalog'
        login_session['username'] = username
        login_session['user_id'] = user.id
        return redirect(url_for('home', status='success'))


# google connect decorator.
# verify validity of google connection.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later usex .
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    print 'username'
    print login_session['username']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height:'
    '300px;border-radius: 150px;-webkit-border-radius:'
    '150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's
# token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400)
        )
        response.headers['Content-Type'] = 'application/json'
        return response


# facebook connect auth decorator.
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(
            json.dumps('Invalid state parameter.'),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read()
    )['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').
        read())['web']['app_secret']
    url = "https://graph.facebook.com/oauth/access_token"
    "?grant_type=fb_exchange_token&client_id="
    "%s&client_secret=%s&fb_exchange_token=%s" % (
        app_id, app_secret, access_token
    )
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
    Due to the formatting for the result from the server
    token exchange we have to split the token first on commas
    and select the first index which gives us the key : value
    for the server access token then we split it on colons
    to pull out the actual token value and replace the remaining
    quotes with nothing so that it can be used directly in the
    graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?'
    'access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the \
    # login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?'
    'access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    'border-radius: 150px;-webkit-border-radius: 150px;'
    '-moz-border-radius: 150px;">'

    flash("Now logged in as %s" % login_session['username'])
    return output


# facebook disconnect decorator.
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?'
    'access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# User Helper Functions
def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# Disconnect based on provider
# three conditions: fb, google, raw.
# the login_sesssion will be modified to let system know
# login status
@app.route('/disconnect')
def disconnect():
    g.user = None
    if 'provider' in login_session:
        if login_session['provider'] == 'itemcatalog':
            del login_session['username']
            del login_session['provider']
            del login_session['user_id']
            return redirect(url_for('home', status='success'))
        else:
            if login_session['provider'] == 'google':
                gdisconnect()
                del login_session['gplus_id']
                del login_session['access_token']
            if login_session['provider'] == 'facebook':
                fbdisconnect()
                del login_session['facebook_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
            flash("You have successfully been logged out.")
            return redirect(url_for('home', status='success'))
    else:
        flash("You were not logged in")
        return redirect(url_for('home', status='fail'))


# edit catalog function.
# modify the property of the catalog
@app.route('/home/<int:owner_id>/edit', methods=['GET', 'POST'])
def editOwner(owner_id):
    if 'username' not in login_session:
        return redirect(url_for('showItem',
                                owner_id=owner_id,
                                status='no access'
                                ))
    else:
        owner = session.query(Owner).filter_by(id=owner_id).first()
        if login_session['user_id'] == owner.user_id:
            if request.method == 'GET':
                return render_template('editowner.html', owner=owner)
            elif request.method == 'POST':
                name = request.form['name']
                owner.name = name
                session.commit()
                return redirect(url_for('showItem',
                                        owner_id=owner_id, status='success'))
        else:
            return redirect(url_for('showItem',
                                    owner_id=owner_id, status='no access'))


# delete owner function.
# if success redirect to home.
# or not still to show item page.
@app.route('/home/<int:owner_id>/delete', methods=['POST'])
def deleteOwner(owner_id):
    if 'username' not in login_session:
        return redirect(url_for('showItem',
                                owner_id=owner_id, status='no access'))
    else:
        owner = session.query(Owner).filter_by(id=owner_id).first()
        if login_session['user_id'] == owner.user_id:
            if request.method == 'POST':
                owners = session.query(Owner).filter_by(id=owner_id).all()
                items = session.query(Item).filter_by(owner_id=owner_id).all()
                for owner in owners:
                    session.delete(owner)
                for item in items:
                    session.delete(item)
                session.commit()
                return redirect(url_for('home', status='success'))
        else:
            return redirect(url_for('showItem',
                                    owner_id=owner_id, status='no access'))


# create new catalog function
# redirect to home. status stand for its success or not.
@app.route('/home/new', methods=['GET', 'POST'])
def newOwner():
    if 'user_id' not in login_session:
        return redirect(url_for('home', status='no access'))
    else:
        if request.method == 'GET':
            return render_template('newowner.html')
        elif request.method == 'POST':
            name = request.form["name"]
            if session.query(Owner).filter_by(name=name).count() == 0:
                owner = Owner(name=name, user_id=login_session['user_id'])
                session.add(owner)
                session.commit()
            return redirect(url_for('home', status='success'))


# show items under certain catalog.
# itemin: the items can be edited by user who created them
# itemout: the items cannot be edited by that user.
@app.route('/home/<int:owner_id>', methods=['GET', 'POST'])
def showItem(owner_id):
    owner = session.query(Owner).filter_by(id=owner_id).one()
    item = session.query(Item).filter_by(owner_id=owner.id).all()
    status = request.args.get('status', '')
    if request.method == 'GET':
        if 'username' not in login_session:
            items = session.query(Item).filter_by(owner_id=owner_id).all()
            return render_template('item.html',
                                   owner=owner,
                                   itemsout=items,
                                   logged=False,
                                   status=status
                                   )
        else:
            # get items created by that user.
            itemin = session.query(Item)\
                            .join(User, User.id == Item.user_id)\
                            .filter(User.name == login_session['username'])\
                            .filter(Item.owner_id == owner_id)\
                            .all()
            # get items not created by that user.
            itemout = session.query(Item)\
                             .join(User, User.id == Item.user_id)\
                             .filter(User.name != login_session['username'])\
                             .filter(Item.owner_id == owner_id)\
                             .all()
            user = session.query(User)\
                          .filter_by(name=login_session['username']).first()
            belong = False
            if owner.user_id == user.id:
                belong = True
            print belong
            return render_template('item.html',
                                   owner=owner, items=itemin,
                                   itemsout=itemout, logged=True,
                                   status=status, belong=belong)
    elif request.method == 'POST':
        if 'user_id' not in login_session:
            return redirect(url_for('showItem',
                                    owner_id=owner_id,
                                    status='no access'
                                    ))
        else:
            # add new itme into db.
            name = request.form["name"]
            description = request.form["description"]
            rate = request.form["rate"]
            price = request.form["price"]
            item = Item(name=name, description=description,
                        rate=rate, price=price, owner_id=owner.id,
                        user_id=login_session['user_id']
                        )
            session.add(item)
            session.commit()
            return redirect(url_for('showItem',
                                    owner_id=owner_id, status='success'))


# show certain item info.
@app.route('/home/<int:owner_id>/<int:item_id>')
@ratelimit.ratelimit(limit=5, per=1*1)
def ItemInfo(owner_id, item_id):
    owner = session.query(Owner).filter_by(id=owner_id).first()
    item = session.query(Item).filter_by(id=item_id).first()
    return render_template('itemInfo.html', owner=owner, item=item)


# edit certain item.
# Get request will return editpage
# POST request will redirect to show item page.
@app.route('/home/<int:owner_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(owner_id, item_id):
    item = session.query(Item).filter_by(id=item_id).first()
    if 'user_id' not in login_session:
        return redirect(url_for('showItem',
                                owner_id=owner_id, status='no access'))
    else:
        if item.user_id != login_session['user_id']:
            return redirect(url_for('showItem',
                                    owner_id=owner_id, status='no access'))
        else:
            if request.method == 'GET':
                return render_template('edititem.html', item=item)
            elif request.method == 'POST':
                name = request.form["name"]
                description = request.form["description"]
                rate = request.form["rate"]
                price = request.form["price"]
                item.name = name
                item.description = description
                item.rate = rate
                item.price = price
                session.commit()
                return redirect(url_for('showItem',
                                        owner_id=owner_id, status='success'))


# delete certain item.
# status reflect delete success or not.
@app.route('/home/<int:owner_id>/<int:item_id>/delete')
def deleteItem(owner_id, item_id):
    item = session.query(Item).filter_by(id=item_id).first()
    if 'user_id' not in login_session:
        return redirect(url_for('showItem',
                                owner_id=owner_id, status='no access'))
    else:
        if item.user_id != login_session['user_id']:
            return redirect(url_for('showItem',
                                    owner_id=owner_id, status='no access'))
        else:
            if item.user_id != login_session['user_id']:
                return redirect(url_for('showItem',
                                        owner_id=owner_id, status='no access'))
            else:
                session.delete(item)
                session.commit()
                return redirect(url_for('showItem',
                                        owner_id=owner_id, status='sucess'))


# JSON end point for a certain catalog.
# return a all items under that catalog.
@app.route('/home/<int:owner_id>/JSON')
@auth.login_required
def ItemsJSON(owner_id):
    owner = session.query(Owner).filter_by(id=owner_id).one()
    item = session.query(Item).filter_by(owner_id=owner.id).all()
    return jsonify(Items=[i.serialize for i in item])


# JSON end point for a certain item.
# return an item.
@app.route('/home/<string:owner_name>/<string:item_name>/JSON')
@auth.login_required
def ItemJSON(owner_name, item_name):
    item = session.query(Item)\
                  .join(Owner, Owner.id == Item.owner_id)\
                  .filter(Owner.name == owner_name, Item.name == item_name)\
                  .one()
    return jsonify(Items=item.serialize)


# JSON end point token.
# should be used to simplify and securify network connectino.
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


if __name__ == "__main__":
    app.secret_key = 'olaolaolaola'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
