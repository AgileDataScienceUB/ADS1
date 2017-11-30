from flask import Flask, make_response,request 
from flask import render_template
from flask_pymongo import PyMongo
from flask import abort, jsonify, redirect, render_template
from flask import request, url_for
from .forms import ProductForm
from bson.objectid import ObjectId
from flask_login import LoginManager, current_user
from flask_login import login_user, logout_user
from flask_login import login_required

from .forms import LoginForm
from .forms import RegistrationForm
from .model import User
from .model import Users
from .model import Recipes
from .model import Ratings

import json

import bson
import pandas as pd

import os

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'app'
app.config['MONGO_URI'] = "mongodb://god:god@ds113938.mlab.com:13938/app"
app.config['SECRET_KEY'] = 'alsfkdgasdlkgja12345378' # Create your own.
app.config['SESSION_PROTECTION'] = 'strong'

mongo = PyMongo(app)

# Use Flask-Login to track current user in Flask's session.
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'

recipes = Recipes().getRecipes()

#mongo = PyMongo(app)


@login_manager.user_loader
def load_user(username):
	"""Flask-Login hook to load a User instance from ID."""
	u = mongo.db.users.find_one({"username": username})
	if not u:
  		return None	
	return User(u['username'])

@app.errorhandler(404)
def error_not_found(error):
  	return render_template('error/not_found.html'), 404

@app.errorhandler(bson.errors.InvalidId)
def error_not_found(error):
	return render_template('error/not_found.html'), 404

@app.route('/login/', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('recipes_list'))
	form = LoginForm(request.form)
	error = None
	if request.method == 'POST' and form.validate():
		username = form.username.data.lower().strip()
		password = form.password.data.lower().strip()
		user = mongo.db.users.find_one({"username": form.username.data})
		if user and User.validate_login(user['password'], form.password.data):
			user_obj = User(user['username'])
			login_user(user_obj)
			return redirect(url_for('user', username=username))
		else:
			error = 'Incorrect username or password.'
	return render_template('user/login.html', form=form, error=error)


@app.route('/logout/')
def logout():
  logout_user()
  return redirect(url_for('recipes_list'))

@app.route('/registration/', methods=['GET', 'POST'])
def registration():
	if current_user.is_authenticated:
		print("Loguejat")
		return redirect(url_for('products_list'))
	form = RegistrationForm(request.form)
	print("form")
	error = None
	if request.method == 'POST' and form.validate():
		print("post")
		a = 0
		username = form.username.data.lower().strip()
		password = form.password.data.lower().strip()
		user = Users().addUser(username, password,'','','')
		#validation of registration and post to mongo

	return render_template('user/registration.html', form=form, error=error)


@app.route('/')
def index():
  	return redirect(url_for('recipes_list'))

@app.route('/recipes/', methods=['GET', 'POST'])
def recipes_list():
	recipes_filter = recipes
	if request.method == 'POST':
		try:
			vegan = request.form['vegan']
			italian = request.form['italian']
		except:
			vegan=False
			italian = False
		time = request.form['time']
		ingredients = request.form['ingredients']
		search = request.form['search']
		recipes_filter = Recipes().getFilteredRecipes(search, time, ingredients)
		#filter
	
	return render_template('recipes/index.html', recipes=recipes_filter.head(100))


@app.route('/recipes/<recipe_name>/')
def recipe_detail(recipe_name):
	recipe = Recipes().getRecipe(recipe_name)
	rating = 3.5
	return render_template('recipes/detail.html', recipe=recipe, recipe_name=recipe_name, rating=rating)

@app.route('/user/<username>/')
@login_required
def user(username):
	return render_template('user/user.html')

# Hack to render style sheets
app.static_folder = 'static'

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)