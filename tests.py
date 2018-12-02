import unittest, random, sys
from app import app

sys.stderr = open('tests.txt', 'w') 

class TestCookBookApp(unittest.TestCase):

    # Ensure Flask has been set up correctly
    def test_flask(self):
        app.app_context
        client = app.test_client(self)
        response = client.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Log in page content loads correctly
    def test_login_page_loaded(self):
        client = app.test_client(self)
        response = client.get('/login', content_type='html/text')
        self.assertTrue(b'<h6 class="center-align">Log In</h6>' in response.data)
        self.assertTrue(b'<button class="btn waves-effect waves-light" type="submit" name="action">Log In' in response.data)

    # Login responds correctly with correct credentials
    def test_valid_login(self):
        client = app.test_client(self)
        response = client.post('/login', data={'username':"test", 'pass':"test"}, follow_redirects=True)
        self.assertIn(b'<h4 class="center-align">Top 5 Recipes</h4>', response.data)
        client.get('/logout', content_type='html/text')

    # Login responds correctly with incorrect credentials
    def test_invalid_login(self):
        client = app.test_client(self)
        response = client.post('/login', data={'username':"xxx", 'pass':"xxx"}, follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

    # Verify that log out works as expected if logged in
    def test_logout_whilst_logged_in(self):
        client = app.test_client(self)
        client.post('/login', data={'username':"test", 'pass':"test"}, follow_redirects=True)
        response = client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been signed out', response.data)

    # Verify that log out is ignored if already logged out
    def test_logout_whilst_logged_out(self):
        client = app.test_client(self)
        response = client.get('/logout', content_type='html/text')
        self.assertIn(b'You have already signed out', response.data)

    # Register page content loads correctly
    def test_register_page_loaded(self):
        client = app.test_client(self)
        response = client.get('/register', content_type='html/text')
        self.assertTrue(b'<h6 class="center-align">Register</h6>' in response.data)
        self.assertTrue(b'<button class="btn waves-effect waves-light" type="submit" name="action">Register' in response.data)

    # Register registers a new user correctly while logged out
    def test_new_user_registration(self):
        client = app.test_client(self)
        response = client.post('/register', data={'username':"test_new" + str(random.randint(1,1000)), 'pass':"test"}, follow_redirects=True)
        self.assertIn(b'<h4 class="center-align">Top 5 Recipes</h4>', response.data)
        client.get('/logout', content_type='html/text')

    # Register does not register an existing user 
    def test_existing_user_registration(self):
        client = app.test_client(self)
        client.post('/login', data={'username':"test", 'pass':"test"}, follow_redirects=True)
        response = client.post('/register', data={'username':"test_new", 'pass':"test"}, follow_redirects=True)
        self.assertIn(b'<h5 class="center-align">You are already logged in and registered</h5>', response.data)
        client.get('/logout', content_type='html/text')

    # Check that a specific recipe already added to favourites for a logged in user
    # results in a "remove from favourites" prompt
    def test_deny_duplicate_favourite(self):
        client = app.test_client(self)
        client.post('/login', data={'username':"test", 'pass':"test"}, follow_redirects=True)
        response = client.post('/add-favourite/5b4366ea22142e9eb80eb610', follow_redirects=True)
        self.assertIn(b'Remove from favourites', response.data)
        client.get('/logout', content_type='html/text')

    # Check that a specific recipe is added to favourites for a logged in user
    def test_add_favourite(self):
        client = app.test_client(self)
        client.post('/login', data={'username':"test", 'pass':"test"}, follow_redirects=True)
        client.post('/remove-favourite/5b4366ea22142e9eb80eb610', follow_redirects=True)
        response = client.post('/add-favourite/5b4366ea22142e9eb80eb610', follow_redirects=True)
        self.assertIn(b'<div class="card-content">', response.data)
        self.assertIn(b'<h3>Seabass</h3>', response.data)
        client.get('/logout', content_type='html/text')

    # Test that favourites are not listed if the user is logged out
    def test_favourites_logged_out(self):
        client = app.test_client(self)
        response = client.get('/favourites', content_type='html/text')
        self.assertIn(b'Please log in or register to view your favourites', response.data)

    # Test that "no favourites" is advised if the user is logged in but has no favourites
    def test_no_favourites(self):
        client = app.test_client(self)
        client.post('/login', data={'username':"test_no_faves", 'pass':"test"}, follow_redirects=True)
        response = client.get('/favourites', content_type='html/text')
        self.assertIn(b'You have no favourites', response.data)
        client.get('/logout', content_type='html/text')

    # Test that "no favourites" is advised if the user is logged in and has favourites
    def test_list_favourites(self):
        client = app.test_client(self)
        client.post('/login', data={'username':"test_new", 'pass':"test"}, follow_redirects=True)
        response = client.get('/favourites', content_type='html/text')
        self.assertIn(b'<span class="card-title recipe-list-item-title">Rump Steak</span>', response.data)
        client.get('/logout', content_type='html/text')

    # Recipe is successfully added for a logged in user
    def test_add_recipe(self):
        client = app.test_client(self)
        client.post('/login', data={'username':"test", 'pass':"test"}, follow_redirects=True)
        client.post('/add-recipe', 
                    data={'recipe_title':"Test Recipe", 'category_name':"meat",
                    'subcategory_name':"beef", 'recipe_description': "test description",
                    'recipe_steps': "1,2,3", 'ingredients': "a,b,c",
                    'cooking_time': "1", 'preparation_time': "2", 'image_url': ''}, 
                    follow_redirects=True)
        response = client.get('/categories/meat/beef', content_type='html/text')
        self.assertIn(b'Test Recipe', response.data)
        self.assertIn(b'test description', response.data)
        client.get('/logout', content_type='html/text')

    # View recipe shows the expected content
    def test_view_recipe(self):
        client = app.test_client(self)
        response = client.get('/view/5b43b0251ae6b6ab5dc2eddc', content_type='html/text')
        self.assertIn(b'Chocolate cake', response.data)

    # Search for a specific recipe returns the relevant recipe and no other recipes
    def test_search(self):
        client = app.test_client(self)
        response = client.post('/search', data={'search':"peas"}, follow_redirects=True)
        self.assertIn(b'Search Results', response.data)
        self.assertIn(b'Pea and cabbage', response.data)
        self.assertNotIn(b'Roast Beef', response.data)

if __name__ == '__main__':
    unittest.main()