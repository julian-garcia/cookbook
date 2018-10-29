def add_new_recipe(request_form, username):
    recipe_steps = request_form['recipe_steps'].split('\n')
    ingredients = request_form['ingredients'].split('\n')
    image_url = request_form['image_url'].replace(' ','_')
    return   {'category_name': request_form['category_name'],
              'subcategory_name': request_form['subcategory_name'],
              'recipe_title': request_form['recipe_title'],
              'recipe_description': request_form['recipe_description'],
              'recipe_steps': recipe_steps,
              'ingredients': ingredients,
              'recipe_author': username,
              'preparation_time': request_form['preparation_time'],
              'cooking_time': request_form['cooking_time'],
              'image_url': image_url}

def edit_existing_recipe(request_form, the_recipe):
    recipe_steps = request_form['recipe_steps'].split('\n')
    ingredients = request_form['ingredients'].split('\n')
    if request_form["image_url"] == "":
        image_url = the_recipe['image_url']
    else:
        image_url = request_form["image_url"].replace(' ','_')
    return   {'recipe_title': request_form["recipe_title"],
              'category_name': request_form["category_name"],
              'subcategory_name': request_form["subcategory_name"],
              'recipe_description': request_form["recipe_description"],
              'recipe_steps': recipe_steps,
              'ingredients': ingredients,
              'cooking_time': request_form["cooking_time"],
              'preparation_time': request_form["preparation_time"],
              'image_url': image_url}
