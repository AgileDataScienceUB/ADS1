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
from .model import User

import json

import bson

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'ads'
app.config['MONGO_URI'] = 'mongodb://mbrufau:hola@ds063725.mlab.com:63725/ads'
app.config['SECRET_KEY'] = 'alsfkdgasdlkgja12345378' # Create your own.
app.config['SESSION_PROTECTION'] = 'strong'

# Use Flask-Login to track current user in Flask's session.
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'

mongo = PyMongo(app)

@login_manager.user_loader
def load_user(user_id):
	"""Flask-Login hook to load a User instance from ID."""
	u = mongo.db.users.find_one({"username": user_id})
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
		return redirect(url_for('products_list'))
	form = LoginForm(request.form)
	error = None
	if request.method == 'POST' and form.validate():
		username = form.username.data.lower().strip()
		password = form.password.data.lower().strip()
		user = mongo.db.users.find_one({"username": form.username.data})
		if user and User.validate_login(user['password'], form.password.data):  
			user_obj = User(user['username'])
			login_user(user_obj)
			return redirect(url_for('products_list'))
		else:
			error = 'Incorrect username or password.'
	return render_template('user/login.html', form=form, error=error)

@app.route('/logout/')
def logout():
  logout_user()
  return redirect(url_for('products_list'))

@app.route('/registration/', methods=['GET', 'POST'])
def registration():
	if current_user.is_authenticated:
		return redirect(url_for('products_list'))
	form = RegistrationForm(request.form)
	error = None
	if request.method == 'POST' and form.validate():
		a = 0
		#validation of registration and post to mongo
	return render_template('user/login.html', form=form, error=error)


@app.route('/')
def index():
  	return redirect(url_for('recipes_list'))

@app.route('/recipes/')
def recipes_list():
  	return render_template('recipes/index.html')

@app.route('/recipes/<recipe_id>/')
def recipe_detail(recipe_id):
	return render_template('recipes/detail.html')

@app.route('/user/<user_id>/')
@login_required
def user(user_id):
	return render_template('user/user.html')