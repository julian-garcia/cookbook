import os, bcrypt
from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mongo = PyMongo(app)

@app.route('/')
def index():
    recipes = mongo.db.recipes.find()
    return render_template('index.html', recipes=recipes);

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name': request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                return redirect(url_for('index'))

        return render_template('login.html', message='Invalid username or password')

    return render_template('login.html', message='')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if request.form['username'] and request.form['pass']:
            if existing_user is None:
                hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'name': request.form['username'], 'password': hashpass})
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            return render_template('register.html', message='User already exists')
        return render_template('register.html', message='Enter a username and password')

    return render_template('register.html', message='')

if __name__ == '__main__':
    app.run(os.getenv('IP'), os.getenv('PORT'), debug=True)
