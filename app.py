import os, bcrypt
from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

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
            return render_template('register.html', message='User ' + existing_user + ' already exists')
        return render_template('register.html', message='Enter a username and password')
    return render_template('register.html', message='')

@app.route('/<category_name>', methods=['GET'])
def list_category(category_name):
    recipes = mongo.db.recipes.find({'category_name': category_name})
    return render_template('recipes.html', recipes=recipes)

@app.route('/<category_name>/<subcategory_name>', methods=['GET'])
def list_subcategory(category_name, subcategory_name):
    recipes = mongo.db.recipes.find({'category_name': category_name, 'subcategory_name': subcategory_name})
    return render_template('recipes.html', recipes=recipes)

@app.route('/add-recipe', methods=['GET', 'POST'])
def add_recipe():
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")
    if request.method == 'POST':
        if 'username' in session:
            recipe_steps = request.form['recipe_steps'].split('\n')
            new_recipe = {'category_name': request.form['category_name'],
                          'subcategory_name': request.form['subcategory_name'],
                          'recipe_title': request.form['recipe_title'],
                          'recipe_description': request.form['recipe_description'],
                          'recipe_steps': recipe_steps,
                          'recipe_author': session['username'],
                          'preparation_time': request.form['preparation_time'],
                          'cooking_time': request.form['cooking_time'],
                          'image_url': request.form['image_url']}
            mongo.db.recipes.insert(new_recipe)
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
        return render_template('login.html', message='Please log in or register to add a recipe')
    return render_template('addrecipe.html', categories=categories, subcategories=subcategories)

@app.route('/view/<recipe_id>', methods=['POST','GET'])
def view_recipe(recipe_id):
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    print('recipe_id')
    return render_template('viewrecipe.html', recipe=the_recipe)

if __name__ == '__main__':
    app.run(os.getenv('IP'), os.getenv('PORT'), debug=True)
