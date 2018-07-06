import os, bcrypt, math
from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
from flask_paginate import Pagination, get_page_parameter, get_page_args
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mongo = PyMongo(app)

@app.route('/')
def index():
    recipes = mongo.db.recipes.find()
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")
    return render_template('index.html',
                           recipes=recipes, categories=categories, subcategories=subcategories);

@app.route('/login', methods=['GET', 'POST'])
def login():
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")

    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name': request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        return render_template('login.html', message='Invalid username or password',
                               categories=categories, subcategories=subcategories)
    return render_template('login.html', message='',
                           categories=categories, subcategories=subcategories)

@app.route('/register', methods=['GET','POST'])
def register():
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if request.form['username'] and request.form['pass']:
            if existing_user is None:
                hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'name': request.form['username'], 'password': hashpass})
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            return render_template('register.html',
                                   message='User ' + str(existing_user['name']) + ' already exists',
                                   categories=categories, subcategories=subcategories)
        return render_template('register.html',
                                message='Enter a username and password',
                                categories=categories, subcategories=subcategories)
    return render_template('register.html', message='',
                            categories=categories, subcategories=subcategories)

def paginate_setup(records):
   global page, per_page, offset, pagination
   page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
   pagination = Pagination(page=page, per_page=per_page,
                           total=records.count(),
                           record_name='recipes',
                           format_total=True, format_number=True)

@app.route('/<category_name>', methods=['GET'])
def list_category(category_name):
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")
    recipes = mongo.db.recipes.find({'category_name': category_name})
    paginate_setup(recipes)
    return render_template('recipes.html',
                           recipes=recipes, categories=categories, subcategories=subcategories,
                           pagination=pagination, page=page, per_page=per_page)

@app.route('/<category_name>/<subcategory_name>', methods=['GET'])
def list_subcategory(category_name, subcategory_name):
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")
    recipes = mongo.db.recipes.find({'category_name': category_name, 'subcategory_name': subcategory_name})
    paginate_setup(recipes)
    return render_template('recipes.html',
                           recipes=recipes, categories=categories, subcategories=subcategories,
                           pagination=pagination, page=page, per_page=per_page)

@app.route('/add-recipe', methods=['GET', 'POST'])
def add_recipe():
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")
    if request.method == 'POST':
        if 'username' in session:
            recipe_steps = request.form['recipe_steps'].split('\n')
            ingredients = request.form['ingredients'].split('\n')
            image_url = request.form['image_url'].replace(' ','_')
            new_recipe = {'category_name': request.form['category_name'],
                          'subcategory_name': request.form['subcategory_name'],
                          'recipe_title': request.form['recipe_title'],
                          'recipe_description': request.form['recipe_description'],
                          'recipe_steps': recipe_steps,
                          'ingredients': ingredients,
                          'recipe_author': session['username'],
                          'preparation_time': request.form['preparation_time'],
                          'cooking_time': request.form['cooking_time'],
                          'image_url': image_url}
            mongo.db.recipes.insert(new_recipe)
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            recipes = mongo.db.recipes.find({'category_name': request.form["category_name"],
                                             'subcategory_name': request.form["subcategory_name"]})
            paginate_setup(recipes)
            return render_template('recipes.html',
                                   recipes=recipes, categories=categories, subcategories=subcategories,
                                   pagination=pagination, page=page, per_page=per_page)

        return render_template('login.html',
                               message='Please log in or register to add a recipe',
                               categories=categories, subcategories=subcategories)
    return render_template('addrecipe.html', categories=categories, subcategories=subcategories)

@app.route('/view/<recipe_id>', methods=['POST','GET'])
def view_recipe(recipe_id):
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")

    return render_template('viewrecipe.html',
                           recipe=the_recipe, categories=categories, subcategories=subcategories, message='')

@app.route('/edit/<recipe_id>', methods=['POST','GET'])
def edit_recipe(recipe_id):
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")

    if 'username' in session:
        the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
        steps = '\n'.join(the_recipe['recipe_steps'])
        ingredients = '\n'.join(the_recipe['ingredients'])

        if request.method == 'POST':
            recipe_steps = request.form['recipe_steps'].split('\n')
            ingredients = request.form['ingredients'].split('\n')
            if request.form["image_url"] == "":
                image_url = the_recipe['image_url']
            else:
                image_url = request.form["image_url"].replace(' ','_')
            update_recipe =  {'recipe_title': request.form["recipe_title"],
                              'category_name': request.form["category_name"],
                              'subcategory_name': request.form["subcategory_name"],
                              'recipe_description': request.form["recipe_description"],
                              'recipe_steps': recipe_steps,
                              'ingredients': ingredients,
                              'cooking_time': request.form["cooking_time"],
                              'preparation_time': request.form["preparation_time"],
                              'image_url': image_url}

            mongo.db.recipes.update({'_id': ObjectId(recipe_id)}, update_recipe)
            if 'file' in request.files:
                file = request.files['file']
                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            recipes = mongo.db.recipes.find({'category_name': request.form["category_name"],
                                             'subcategory_name': request.form["subcategory_name"]})
            paginate_setup(recipes)
            return render_template('recipes.html',
                                   recipes=recipes, categories=categories, subcategories=subcategories,
                                   pagination=pagination, page=page, per_page=per_page)

        return render_template('editrecipe.html',
                               recipe=the_recipe, categories=categories,
                               subcategories=subcategories, steps=steps, ingredients=ingredients)
    return render_template('login.html',
                           message='Please log in or <a href="' + url_for('register') + '">register</a> to edit a recipe',
                           categories=categories, subcategories=subcategories)

@app.route('/add-favourite/<recipe_id>', methods=['GET', 'POST'])
def add_favourite(recipe_id):
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")
    if 'username' in session:
        the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
        new_favourite = {'user': session['username'],
                         'recipe_id': the_recipe['_id']}
        existing_favourite = mongo.db.favourites.find_one(new_favourite)
        if existing_favourite is None:
            if request.method == 'POST':
                mongo.db.favourites.insert_one(new_favourite)

                return render_template('viewrecipe.html',
                                       recipe=the_recipe, categories=categories, subcategories=subcategories,
                                       message='Recipe added to your favourites')

            return render_template('addfavourite.html',
                                  recipe=the_recipe, categories=categories, subcategories=subcategories)

        return render_template('removefavourite.html',
                               recipe=the_recipe, categories=categories, subcategories=subcategories)

    return render_template('login.html',
                           message='Please log in or register to add a favourite',
                           categories=categories, subcategories=subcategories)

@app.route('/remove-favourite/<recipe_id>', methods=['POST','GET'])
def remove_favourite(recipe_id):
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")

    if 'username' in session:
        the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
        if request.method == 'POST':
            delete_favourite = {'user': session['username'],
                                'recipe_id': the_recipe['_id']}
            mongo.db.favourites.remove(delete_favourite)

            return render_template('viewrecipe.html',
                                   recipe=the_recipe, categories=categories, subcategories=subcategories,
                                   message='Recipe removed from your favourites')

        return render_template('removefavourite.html',
                               recipe=the_recipe, categories=categories, subcategories=subcategories)

    return render_template('login.html',
                           message='Please log in or register to remove a favourite',
                           categories=categories, subcategories=subcategories)

if __name__ == '__main__':
    app.run(os.getenv('IP'), os.getenv('PORT'), debug=True)
