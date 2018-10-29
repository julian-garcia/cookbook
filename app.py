import os, bcrypt, math, pymongo
from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
from flask_paginate import Pagination, get_page_parameter, get_page_args
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from chart import generate_top5_data
from recipe import add_new_recipe, edit_existing_recipe

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mongo = PyMongo(app)

def get_categories():
    global categories, subcategories
    categories = mongo.db.categories.find().sort("category_name")
    subcategories = mongo.db.subcategories.find().sort("subcategory_name")

@app.route('/')
def index():
    '''
    Home page - basic summary figures and a d3/dc based chart
    representation of the most popular recipes
    '''
    get_categories()
    recipes = mongo.db.recipes.find()
    favourites = mongo.db.favourites.find()
    count_recipes = recipes.count()
    count_favourites = favourites.count()
    count_users = mongo.db.users.find().count()

    # Identify all favourited recipies and extract their titles and ids
    list_favourites = list(favourites.sort("recipe_id"))
    ids = [item['recipe_id'] for item in list_favourites]
    list_recipes, recipe_ids = zip(*[(item['recipe_title'], item['_id'])
                        for item in list(mongo.db.recipes.find({'_id': {'$in': ids}}).sort("_id"))])

    popular = generate_top5_data(list_favourites, list_recipes, recipe_ids)

    return render_template('index.html',
                           recipes=recipes, categories=categories, subcategories=subcategories,
                           count_favourites=count_favourites, count_recipes=count_recipes,
                           count_users=count_users, popular_recipes=popular['popular_recipes'],
                           popular_links=popular['popular_links']);

@app.route('/search', methods=['POST'])
def search():
    '''
    Basic recipe title text search performed by the search field in the nav bar
    '''
    get_categories()
    if request.method == 'POST':
        mongo.db.recipes.create_index([('recipe_title', 'text')])
        recipes = mongo.db.recipes.find({"$text": {"$search": request.form['search']}})
        if recipes.count() == 0:
            return render_template('usermessage.html',
                                   categories=categories, subcategories=subcategories,
                                   message='No recipes found')

        paginate_setup(recipes)
        return render_template('recipes.html',
                               recipes=recipes, categories=categories, subcategories=subcategories,
                               pagination=pagination, page=page, per_page=per_page,
                               page_title='Search Results')

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    User Authentication - check user credentials against custom mongodb user collection
    using bcrypt for secure password comparison. Store user name as a global session variable
    which should clear out when the browser is closed or browser history is cleared.
    Other routes can then refer to the session variable to determine who is logged in.
    '''
    get_categories()

    # Check that the user hasn't already logged in and, if so,
    # do not route to the login form and advise the user
    if 'username' in session:
        return render_template('usermessage.html',
                               categories=categories, subcategories=subcategories,
                               message='You are already logged in')

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

@app.route('/logout')
def logout():
    get_categories()

    if 'username' in session:
        session.pop('username')
        return render_template('usermessage.html',
                               categories=categories, subcategories=subcategories,
                               message='You have been signed out <i class="fas fa-sign-out-alt"></i>')

    return render_template('usermessage.html',
                           categories=categories, subcategories=subcategories,
                           message='You have already signed out <i class="fas fa-sign-out-alt"></i>')

@app.route('/register', methods=['GET','POST'])
def register():
    '''
    User registration - Create a user in the custom users collection using bcrypt to encrypt
    the password to maintain user account security
    '''
    get_categories()

    # Check that the user hasn't already logged in and therefore is registered.
    # If so, do not route to the registration form and advise the user
    if 'username' in session:
        return render_template('usermessage.html',
                               categories=categories, subcategories=subcategories,
                               message='You are already logged in and registered')

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if request.form['username'] and request.form['pass']:
            # Check for existing user to avoid re-registering the same user
            if existing_user is None:
                hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'name': request.form['username'], 'password': hashpass})
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            return render_template('usermessage.html',
                                   message='User ' + str(existing_user['name']) + ' already exists',
                                   categories=categories, subcategories=subcategories)

        return render_template('usermessage.html',
                                message='Enter a username and password',
                                categories=categories, subcategories=subcategories)

    return render_template('register.html', message='',
                            categories=categories, subcategories=subcategories)

def paginate_setup(records):
    '''
    Using prebuilt flask_paginate extension to generate pagination for the recipe listing
    pages Jinja Looping is then used within the listing template recipes.html to determine
    recipes to be displayed for each page
    '''
    global page, per_page, offset, pagination
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    pagination = Pagination(page=page, per_page=per_page,
                            total=records.count(),
                            record_name='recipes',
                            format_total=True, format_number=True)

@app.route('/categories/<category_name>', methods=['GET'])
def list_category(category_name):
    '''
    Paginated view of all recipes within a defined category
    '''
    get_categories()

    recipes = mongo.db.recipes.find({'category_name': category_name}).sort("recipe_title")
    paginate_setup(recipes)
    return render_template('recipes.html',
                           recipes=recipes, categories=categories, subcategories=subcategories,
                           pagination=pagination, page=page, per_page=per_page,
                           page_title='')

@app.route('/categories/<category_name>/<subcategory_name>', methods=['GET'])
def list_subcategory(category_name, subcategory_name):
    '''
    Paginated view of all recipes within a defined category and subcategory
    '''
    get_categories()

    recipes = mongo.db.recipes.find({'category_name': category_name,
                                     'subcategory_name': subcategory_name}).sort("recipe_title")
    paginate_setup(recipes)
    return render_template('recipes.html',
                           recipes=recipes, categories=categories, subcategories=subcategories,
                           pagination=pagination, page=page, per_page=per_page,
                           page_title='')

@app.route('/add-recipe', methods=['GET', 'POST'])
def add_recipe():
    '''
    Recipe insertion into a mongodb database via pymongo. Checks that the user
    is logged on so that we can populate the recipe author.
    '''
    get_categories()

    if 'username' in session:
        if request.method == 'POST':
            new_recipe = add_new_recipe(request.form, session['username'])
            mongo.db.recipes.insert(new_recipe)

            # Pick up the photo of the recipe and upload to the static area
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('list_subcategory',
                                    category_name=request.form["category_name"],
                                    subcategory_name=request.form["subcategory_name"]))

        return render_template('addrecipe.html', categories=categories, subcategories=subcategories)

    return render_template('login.html',
                           message='Please log in or register to add a recipe',
                           categories=categories, subcategories=subcategories)

@app.route('/view/<recipe_id>', methods=['POST','GET'])
def view_recipe(recipe_id):
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    get_categories()

    return render_template('viewrecipe.html',
                           recipe=the_recipe, categories=categories, subcategories=subcategories, message='')

@app.route('/edit/<recipe_id>', methods=['POST','GET'])
def edit_recipe(recipe_id):
    '''
    Handle single recipe updates. Unlike add_recipe, all fields here are optional as the user
    should be able to change any single detail whilst maintaining the rest as is.
    '''
    get_categories()

    if 'username' in session:
        the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
        steps = '\n'.join(the_recipe['recipe_steps'])
        ingredients = '\n'.join(the_recipe['ingredients'])

        if request.method == 'POST':
            update_recipe = edit_existing_recipe(request.form, the_recipe)
            mongo.db.recipes.update({'_id': ObjectId(recipe_id)}, update_recipe)

            # Pick up the photo of the recipe and upload to the static area
            # In this case, the file is optional so first need to check that
            # a new photo was supplied by the user
            if 'file' in request.files:
                file = request.files['file']
                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('list_subcategory',
                                    category_name=request.form["category_name"],
                                    subcategory_name=request.form["subcategory_name"]))

        return render_template('editrecipe.html',
                               recipe=the_recipe, categories=categories,
                               subcategories=subcategories, steps=steps, ingredients=ingredients)

    return render_template('login.html',
                           message='Please log in or <a href="' + url_for('register') + '">register</a> to edit a recipe',
                           categories=categories, subcategories=subcategories)

@app.route('/add-favourite/<recipe_id>', methods=['GET', 'POST'])
def add_favourite(recipe_id):
    '''
    Add a favourite. Checks that a user is logged on and that the favourite
    is not already among the list of favourites. If a favourite already exists,
    the user is directed to the remove favourite functionality.
    '''
    get_categories()

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
    '''
    Remove a favourite from a users favourites. In this case we don't need to check
    if the favourite is present in the list of favourites as the user is only directed
    here from add_favourite which will have already verified its presence in favourites
    '''
    get_categories()

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

@app.route('/favourites')
def favourites():
    '''
    List user's favourites - similar to the category recipe listing except it determines
    favourite recipe ids and feeds those in to the 'in' operator against the recipes collection
    '''
    get_categories()

    favourites = mongo.db.favourites
    if 'username' in session:
        fav = list(favourites.find({'user': session['username']}))
        if fav == []:
            return render_template('usermessage.html',
                                   categories=categories, subcategories=subcategories,
                                   message='You have no favourites <i class="far fa-frown"></i>')

        ids = [item['recipe_id'] for item in fav]
        recipes = mongo.db.recipes.find({'_id': {'$in': ids}}).sort("recipe_title")
        paginate_setup(recipes)
        return render_template('recipes.html',
                               recipes=recipes, categories=categories, subcategories=subcategories,
                               pagination=pagination, page=page, per_page=per_page,
                               page_title='Favourites')

    return render_template('login.html',
                           message='Please log in or register to view your favourites',
                           categories=categories, subcategories=subcategories)

@app.route('/request_category', methods=['POST','GET'])
def request_category():
    '''
    Request a new category/subcategory combination
    Any logged in user can request a new combination, which is then
    inserted in to a requests collection which is reviewed by an administrator
    and approved or rejected.
    '''
    get_categories()

    if 'username' in session:
        if request.method == 'POST':
            new_cat =  {'category_name': request.form["category_name"],
                        'subcategory_name': request.form["subcategory_name"]}
            existing_category = mongo.db.subcategories.find_one(new_cat)
            already_requested = mongo.db.category_requests.find_one(new_cat)

            if existing_category is None and already_requested is None:
                mongo.db.category_requests.insert_one(new_cat)
                return render_template('requestcategory.html',
                                       categories=categories, subcategories=subcategories,
                                       message='Category requested and awaiting approval');

            return render_template('usermessage.html',
                                   categories=categories, subcategories=subcategories,
                                   message='This category already exists or has already been requested')

        return render_template('requestcategory.html',
                               categories=categories, subcategories=subcategories,
                               message='');

    return render_template('login.html',
                           message='Please log in or register to request a new category',
                           categories=categories, subcategories=subcategories)

@app.route('/list-requests', methods=['GET'])
def list_requests():
    '''
    List all requested category/subcategory combinations. This is only accessible
    by the administrator - in this case this is identified by the user name "admin"
    The nav bar is populated with categories at the top level and subcategories within
    each drop down sub menu. If we leave users to add categories as they please, the menu
    will quickly become overpopulated, hence admin only access.
    '''
    get_categories()

    if 'username' in session:
        if session['username'] == 'admin':
            requests = mongo.db.category_requests.find()

            if requests.count()==0:
                return render_template('usermessage.html',
                                       categories=categories, subcategories=subcategories,
                                       message='No requests are available')

            return render_template('listrequests.html',
                                   categories=categories, subcategories=subcategories,
                                   requests=requests)

        return render_template('usermessage.html',
                               categories=categories, subcategories=subcategories,
                               message='Sorry, you are not authorised to approve category requests')

    return render_template('usermessage.html',
                           categories=categories, subcategories=subcategories,
                           message='You must be logged in to approve category requests')

@app.route('/approve-request', methods=['POST','GET'])
def approve_request():
    '''
    Approve request to add a new category/subcategory combination
    Upon administrator approval, the combination is removed from the
    requests collection and added to the category and subcategory collections
    '''
    get_categories()

    if 'username' in session:
        if session['username'] == 'admin':
            new_cat =  {'category_name': request.form["category_name"]}
            new_subcat =  {'category_name': request.form["category_name"],
                           'subcategory_name': request.form["subcategory_name"]}
            existing_category = mongo.db.categories.find_one(new_cat)
            existing_subcategory = mongo.db.subcategories.find_one(new_subcat)
            mongo.db.category_requests.remove(new_subcat)

            # Only insert the new category and/or subcategory if the category
            # and/or subcategory is not already present in their respective collections
            if existing_category is None:
                mongo.db.categories.insert_one(new_cat)
            if existing_subcategory is None:
                mongo.db.subcategories.insert_one(new_subcat)

            return redirect(url_for('list_requests'))

        return render_template('usermessage.html',
                               categories=categories, subcategories=subcategories,
                               message='Sorry, you are not authorised to approve category requests')

    return render_template('usermessage.html',
                           categories=categories, subcategories=subcategories,
                           message='You must be logged in to approve category requests')

@app.route('/reject-request', methods=['POST','GET'])
def reject_request():
    '''
    Reject a request to add a new category/subcategory combination
    Simply remove from the requests collection without adding to the category collections
    '''
    get_categories()

    if 'username' in session:
        if session['username'] == 'admin':
            new_subcat =  {'category_name': request.form["category_name"],
                           'subcategory_name': request.form["subcategory_name"]}
            mongo.db.category_requests.remove(new_subcat)

            return redirect(url_for('list_requests'))

        return render_template('usermessage.html',
                               categories=categories, subcategories=subcategories,
                               message='Sorry, you are not authorised to reject category requests')

    return render_template('usermessage.html',
                           categories=categories, subcategories=subcategories,
                           message='You must be logged in to reject category requests')

if __name__ == '__main__':
    app.run(os.getenv('IP'), os.getenv('PORT'), debug=True)
