from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/login')
def login():
	return 'Login'

@app.route('/registration')
def registration():
	return 'Registration'

@app.route('/recipes')
def recipes():
	return 'Recipes'

@app.route('/user/<username>')
def user_profile(username):
	return 'User %s' % username
