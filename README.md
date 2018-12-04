# Cookle Bookle
This is a **Flask** based implementation of a customisable cook book. Pages are rendered using **Python** based views, linking backend data (a **mongoDB** database housed by [mlab](https://mlab.com)) to html templates rendered by the browser. A working demo has been deployed via Heroku at this URL: [cookle-bookle.herokuapp.com](https://cookle-bookle.herokuapp.com)

## Features
- All users can view all recipes across various categories and sub-categories
- Registered users can:
  - add, edit, view and browse recipes
  - add/remove favourites
  - request new categories
- Requested categories can be approved/rejected by an administrator
- Home page visualisation of the 5 most favourited recipies

## Design
A rough wireframe was generated using [draw.io](https://www.draw.io). The wireframes can be viewed by
opening [mockup.xml](resources/mockup.xml) via the draw.io website. The colour scheme was defined using
[coolors.co](https://coolors.co), details of the selected scheme are in [palette.pdf](resources/palette.pdf). The design was implemented to be responsive in relation to viewport size, taking a mobile first approach.

## Languages/Framework
- HTML, CSS, SCSS
- [Flask 1.0.2](http://flask.pocoo.org)
- [Python 3.7](https://www.python.org)
- [Materialize 1.0.0-rc.2](https://materializecss.com)
- [jQuery 3.3.1](https://jquery.com)
- [D3 v5](https://d3js.org) (Data driven documents)
- [DC v3.0.4](https://dc-js.github.io/dc.js/) (Dimensional charting)
- [crossfilter v1.3.12](https://github.com/crossfilter/crossfilter/wiki)
- [Fontawesome v5.0.13](https://fontawesome.com)
- [Google Fonts](https://fonts.google.com) (Material icons, Courgette, Overpass, Pacifico)

## Deployment & Contributions
The source code is deployed on GitHub whilst the app itself is deployed on Heroku which is linked to the GitHub repository. To create your own copy of the app, make amendments and re-deploy under your own account, follow the installation and deployment instructions.
### Installation
Make your own folder and navigate to it on the command line. Then enter the following:
```
git clone https://github.com/julian-garcia/cookbook.git
source bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
### Running the app locally
```
python app.py
http://localhost:5000
```
### Deployment (GitHub)
- Navigate to your project directory on the command line and enter `git add .` 
- Enter `git commit -m 'My changes'` - replace 'my changes' with a brief overview of your changes
- Finally deploy using `git push -u origin master`
### Deployment (Heroku)
```
heroku login
heroku apps:create my-app-name
git push -u heroku master
heroku ps:scale web=1
```
Add config vars: IP 0.0.0.0 and PORT 5000

## Testing
Several tests have been determined to verify that database queries and client requests are behaving as expected by checking the resulting page content after specific requests. Test results are in [tests.txt](tests.txt) which shows successful outcomes for the following tests:
- test_add_favourite - New favaourite added to favourites for a logged in user
- test_add_recipe - Test new recipe is added for logged in user
- test_deny_duplicate_favourite - Favourite recipe not added if already favourited
- test_existing_user_registration - Registration attempt ignored if user already exists
- test_favourites_logged_out - Favourites not listed if nobody is logged in
- test_invalid_login - Incorrect details reported if bad password upon logging in
- test_list_favourites - Favourites are listed when a user is logged in and has favourites
- test_login_page_loaded - Check the log in page is loaded as expected
- test_logout_whilst_logged_in - User is able to log out whilst logged in
- test_logout_whilst_logged_out - Recognises that a user is already logged out and tries to log out
- test_new_user_registration - A new user is registered successfully
- test_no_favourites - No favourites message is reported if a user has no favourites
- test_register_page_loaded - Check the user registration page is loaded as expected
- test_search - Verify that search results
- test_valid_login - User is logged in when correct credentials are used
- test_view_recipe - Viewing a specific recipe renders expected content
You can re-run the above tests by running: `python tests.py -v` on the command line, the results will be redirected to [tests.txt](tests.txt). Source code for the tests: [tests.py](tests.py)

## Credits
### Media
Images retrieved from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page) - these are freely reusable images
