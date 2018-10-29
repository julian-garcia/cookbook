import itertools, operator
from operator import itemgetter
from bson.objectid import ObjectId

def generate_top5_data(list_favourites, list_recipes, recipe_ids):
    '''
    This generates dictionary lists containing the top five most popular recipies in terms of the
    number of times they have been favourited by users.
    The data will be used by d3/dc JavaScript to generate a top 5 chart on the home page.
    '''
    # Sum the number of users for each favourited recipe so that we can then determine the 5 most popular
    list_increments = [(item['recipe_id'], 1) for item in list_favourites]
    list_user_counts = []
    it = itertools.groupby(list_increments, operator.itemgetter(0))

    for key, subiter in it:
       list_user_counts.append(sum(item[1] for item in subiter))

    # Form a list of dictionaries that will form the data source for
    # the JS charting framework dc
    popular_recipes = []
    for recipe_id, recipe, users in zip(recipe_ids, list_recipes, list_user_counts):
        # popular_recipes.append({'recipe_id': ObjectId(recipe_id), 'recipe_title': recipe, 'user_count': users})
        popular_recipes.append({'recipe_id': ObjectId(recipe_id), 'recipe_title': recipe, 'user_count': users})

    # Sorting by descending user count primarily and then ascending recipe title
    # Must explicitly define the sort order here so that their order in the bar
    # chart matches the order of the links
    popular_recipes_full = sorted(popular_recipes, key = lambda i: (-i['user_count'], i['recipe_title']))[:5]

    # This is the data that will be passed to d3/dc/crossfilter. JS doesn't like object ids
    # hence their removal
    popular_recipes = [dict((k, v) for k, v in d.items() if k != 'recipe_id') for d in popular_recipes_full]

    # Supply links to the 5 most popular recipes
    popular_links = ['/view/' + str(item['recipe_id'])
                        for item in popular_recipes_full]

    return {'popular_recipes': popular_recipes, 'popular_links': popular_links}
