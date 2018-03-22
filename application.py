# !/usr/bin/env python

from flask import (Flask, render_template, request, redirect,
                    url_for, jsonify, session as login_session,
                    flash)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Category, Item, User
from flask_oauth import OAuth
from urllib2 import Request, urlopen, URLError

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# if you don't scope it, you will have problems and a huge headache
session = scoped_session(DBSession)

# Google login API
GOOGLE_CLIENT_ID = '871061221990-7kuoehpktnhg53ct7j9mb6p6gctu4o05.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '0lKlflnT3wDXC9RUntyd7EgO'
REDIRECT_URL = '/google-oauth-callback'
SECRET_KEY = 'i=H`fe3}DP/be/FyhE:--9v|AdTqt.j@EJlfm/Um?pZ`KJy&(dp7,719WnM})'
DEBUG = True

app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()
google = oauth.remote_app(
    'google',
    base_url='https://www.google.com/accounts/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                          'response_type': 'code'},
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    consumer_key=GOOGLE_CLIENT_ID,
    consumer_secret=GOOGLE_CLIENT_SECRET)

# Create JSON object for Categories
@app.route('/category/JSON')
def categoryJSON():
	category = session.query(Category).all()
	return jsonify(category=[c.serialize for c in category])

# Create JSON object for Item
@app.route('/items/JSON')
def itemJSON():
	item = session.query(Item).all()
	return jsonify(item=[i.serialize for i in item])

# Load main home page
# valid URL for accessing home page
@app.route('/')
def load_main_page():
	all_categories = session.query(Category).all()
	# if already logged in then continue
	if ('name' in login_session):
		logged_in_name = login_session['name']
	else:
		logged_in_name = "Random Stranga"
	return render_template('index.html',
                            categories=all_categories,
                            the_user_name=logged_in_name)

# View items in selected category
# valid URL for viewing items of a category
@app.route('/category/<category_id>')
def view_category_items(category_id):
	all_categories = session.query(Category).all()
	current_category = session.query(Category).filter_by(id=category_id).first()
	# query to retrieve all items under selected category
	items = session.query(Item).filter_by(category_id=category_id).all()
	if ('name' in login_session):
		logged_in_name = login_session['name']
	else:
		logged_in_name = "Random Stranga"
	return render_template('show-items.html',categories=all_categories,items=items
						   ,category=current_category, the_user_name=logged_in_name)

# Add new category
# valid URL for accessing add category page
@app.route('/category/add', methods=['GET', 'POST'])
def add_category():
    if (request.method == 'POST'):	# post to database when user clicks submit
        new_name = request.form['category-name']	# get new category name from form
        new_category = Category(name=new_name, user_id=login_session['id'])
        session.add(new_category)
        session.commit()
        return redirect(url_for('load_main_page', the_user_name=login_session['name']))
    else:
        # check if user is logged in
        if ('name' in login_session):
            all_categories = session.query(Category).all()
            logged_in_name = login_session['name']
            return render_template('add-category.html',
                                    categories=all_categories,
                                    the_user_name=logged_in_name)
        # redirect to login if not logged in
        else:
            return redirect(url_for('login'))

# View categories to delete
# valid URL for viewing categories to delete
@app.route('/category/delete')
def view_categories_to_delete():
    # check if logged in
	if ('name' in login_session):
		logged_in_name = login_session['name']
		deleted_categories = session.query(Category).filter_by(user_id=login_session['id']).all()
		all_categories = session.query(Category).all()
		return render_template('delete-category.html', categories=all_categories,
                                deleted=deleted_categories, the_user_name=logged_in_name)
	else:
		return redirect(url_for('login'))

# Delete category
# valid URL to actually delete category from database
@app.route('/category/<category_id>/delete')
def delete_category_now(category_id):
    if ('name' in login_session):
        category_to_delete = session.query(Category).filter_by(id=category_id).first()
        # check to see if it is your category_id
        if (category_to_delete.user_id != login_session['id']):
            flash("You can only delete categories you created")
        else:
            session.delete(category_to_delete)
            session.commit()
        return redirect(url_for('view_categories_to_delete', the_user_name=login_session['name']))
    else:  # login if not logged in
        return redirect(url_for('login'))

# Add new item
# valid URL to add items
@app.route('/category/<category_id>/add', methods=['GET', 'POST'])
def add_item(category_id):
    if (request.method == 'POST'):
        new_item_name = request.form['item-name']
        new_item_description = request.form['item-description']
        new_item = Item(name=new_item_name,
                        description=new_item_description,
                        category_id=category_id,
                        user_id=login_session['id'])
        session.add(new_item)
        session.commit()
		# redirect to see all items in selected category
        return redirect(url_for('view_category_items',
                        category_id=category_id,
                        category_name=category.name,
                        the_user_name=login_session['name']))
    else:
        if ('name' in login_session):
            all_categories = session.query(Category).all()
            category = session.query(Category).filter_by(id=category_id).first()
            logged_in_name = login_session['name']
            return render_template('add-item.html',
                                    categories=all_categories,
                                    category=category,
                                    the_user_name=logged_in_name)
        else:
            return redirect(url_for('login'))

# Edit item
# valid URL to edit item
@app.route('/category/<category_id>/<item_id>/edit', methods=['GET', 'POST'])
def edit_item(category_id, item_id):
    if (request.method == 'POST'):
        item_to_edit = session.query(Item).filter_by(id=item_id).first()
        # check to see if item was created by user
        if (item_to_edit.user_id != login_session['id']):
            flash("You can only edit your own items")
        else:
            new_name = request.form['item-name']
            new_description = request.form['item-description']
            item_to_edit.name = new_name
            item_to_edit.description = new_description
            session.add(item_to_edit)
            session.commit()
		# redirect to see all items in selected category
        return redirect(url_for('view_category_items', category_id=category_id,
                        the_user_name=login_session['name']))
    else:
        if ('name' in login_session): # check if logged in
            all_categories = session.query(Category).all()
            category = session.query(Category).filter_by(id=category_id).first()
            logged_in_name = login_session['name']
            return render_template('edit-item.html', categories=all_categories,
                                    item=item_to_edit, category=category,
                                    item_id=item_id, the_user_name=logged_in_name)
        else:
            return redirect(url_for('login'))

# Delete item
# valid url to delete item from db
@app.route('/category/<category_id>/<item_id>/delete')
def delete_item(category_id, item_id):
    # check if user is logged in
    if ('name' in login_session):
        item_to_delete = session.query(Item).filter_by(id=item_id).first()
        # check to see if user is the one who created this
        if (item_to_delete.id != login_session['id']):
            flash("You can only delete items you created.")
        else:
            session.delete(item_to_delete)
            session.commit()
        # redirect to see all items in selected category
    	return redirect(url_for('view_category_items',
                                category_id=category_id,
                                the_user_name=login_session['name']))
    else:
        return redirect(url_for('login'))

# Login Page
@app.route('/login')
def login():
	callback=url_for('authorized', _external=True)
	return google.authorize(callback=callback)

# Logout
@app.route('/logout')
def logout():
	# release session variables
	login_session.pop('id', None)
	login_session.pop('name', None)
	return redirect(url_for('load_main_page'))

# Google authorization handler - required
@app.route(REDIRECT_URL)
@google.authorized_handler
def authorized(resp):
	access_token = resp['access_token']
	login_session['access_token'] = access_token, ''
	access_token = login_session.get('access_token')

	access_token = access_token[0]

	headers = {'Authorization': 'OAuth '+access_token}
	req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
	res = urlopen(req)
	# parse response object to get name and email ONLY
	arr = res.read().split(",")
	email_1 = arr[1].split(":")
	name_1 = arr[3].split(":")
	email = email_1[1].replace("\"", "")
	name = name_1[1].replace("\"", "")
	# check database with email to see if user already exists
	user = session.query(User).filter_by(email=email).first()
	if (user is None):	# user not in db, so create new record
		u = User(name=name, email=email)
		session.add(u)
		session.commit()
		# query again to fetch user ID
		user = session.query(User).filter_by(email=email).first()
	# set session variables then go to main page
	login_session['name'] = user.name
	login_session['id'] = user.id

	return redirect(url_for('load_main_page'))

# required for Google OAuth API
@google.tokengetter
def get_access_token():
    return login_session.get('access_token')

# Main method
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
