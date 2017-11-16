from flask import Flask, url_for
from flask import render_template
import os
app = Flask(__name__)

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

@app.route('/')
def index():
    return 'Index Page'

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/registration')
def registration():
	return 'Registration'

@app.route('/recipes')
def recipes():
	name = 'Spagetti'
	return render_template('recipes.html', name=name)

@app.route('/user/<username>')
def user_profile(username):
	return 'User %s' % username
