from flask import Flask, make_response,request 
from flask import render_template
from flask_pymongo import PyMongo
from flask import abort, jsonify, redirect, render_template
from flask import request, url_for
from forms import ProductForm
from bson.objectid import ObjectId
from flask_login import LoginManager, current_user
from flask_login import login_user, logout_user
from flask_login import login_required

from forms import UserForm
from forms import LoginForm
from forms import RegistrationForm
from model import User
from model import Users
from model import Recipes
from model import Ratings
from werkzeug.utils import secure_filename

import json

import bson
import pandas as pd
import numpy as np
#from . import recolib

import os

app = Flask(__name__)
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['MONGO_DBNAME'] = 'app'
app.config['MONGO_URI'] = "mongodb://god:god@ds113938.mlab.com:13938/app"
app.config['SECRET_KEY'] = 'alsfkdgasdlkgja12345378' # Create your own.
app.config['SESSION_PROTECTION'] = 'strong'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mongo = PyMongo(app)

# Use Flask-Login to track current user in Flask's session.
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'

recipeClass = Recipes()
recipes = recipeClass.getRecipes()
recipes['img'] = np.nan
recipes['description'] = np.nan
recipes['pred_rating'] = np.zeros(len(recipes.index))

# It take a lot
a= Users().getUsers()
a = a.set_index("username")
a = a.drop(["_id","allergies","image","name","password"], axis = 1)
a.fillna(0, inplace=True)
#a = Ratings().getRatings()
#a = a[~a.index.duplicated(keep='first')]

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
			allergiesAux = user['allergies']
			print(type(allergiesAux))
			if isinstance(allergiesAux, list):
				allergies = allergiesAux
			else:
				allergies = allergiesAux.split(',')
			recipes = recipeClass.getFilteredRecipes("", 1e6, 1e6, 0, allergies)
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

@app.route('/info')
def info():
	return render_template('info.html')

@app.route('/rateRecipe', methods=['POST'])
def rateRecipe():
	rating = request.form['rating']
	name = request.form['name']
	Users().addRating(current_user.get_id(),name,rating)
	return json.dumps({'status':'OK'});

@app.route('/recipes/', methods=['GET', 'POST'])
def recipes_list():
	username = current_user.get_id()
	recipes_filter = recipes
	recipes_ordered = recipes
	pred_rating = pd.Series([None]*recipes_ordered.shape[0], index = recipes_ordered.index)
	allergies = []
	if username != None:
		user = Users().getUser(username)
		allergiesAux = user['allergies']
		if isinstance(allergiesAux, list):
			allergies = allergiesAux
		else:
			allergies = allergiesAux.split(',')
	if request.method == 'POST':
		time = request.form['time']
		ingredients = request.form['ingredients']
		search = request.form['search']
		recipes_filter = recipeClass.getFilteredRecipes(search, time, ingredients,0, allergies)
		#filter
		if (len(search) > 0 and username!=None):
			recipes_ordered,pred_rating = recipeClass.getRecipesRecommender(recipes_filter,username,a)
		else:
			recipes_ordered = recipes_filter
			pred_rating = pd.Series([None]*recipes_ordered.shape[0], index = recipes_ordered.index)
	rating = 3
	#return render_template('recipes/index.html', recipes=recipes_filter.head(100), rating=rating)
	return render_template('recipes/index.html', recipes=recipes_ordered.head(100), rating=rating, pred_rating=pred_rating.head(100))

@app.route('/recipes/<recipe_name>/')
def recipe_detail(recipe_name):
	username = current_user.get_id()
	recipe = recipeClass.getRecipe(recipe_name)
	img, method, description = recipeClass.getFullRecipe(recipe_name)
	rating = 3
	return render_template('recipes/detail.html', recipe=recipe, recipe_name=recipe_name, rating=rating, img=img, method=method, description=description, username=username)

@app.route('/user/<username>/', methods=['GET', 'POST'])
@login_required
def user(username):
	form = UserForm(request.form)
	error = None
	if request.method == 'POST':
		a = 0
		username = form.username.data.lower().strip()
		name = form.name.data.lower().strip()
		allergies = form.allergies.data.lower().strip()
		user = Users().setUser(username,name,allergies,'')
		#validation of registration and post to mongo
	usero = Users().getUser(username)
	if(usero['username'] == ""):
		error = "User not found"
		return error, 404
	else:
		form.username=usero['username']
		form.name=usero['name']
		form.allergies=usero['allergies']
	

	return render_template('user/user.html', form=form, error=error)


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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filename = 'http://127.0.0.1:5000/uploads/' + filename
    return render_template('template.html', filename = filename)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)