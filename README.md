# Cookle Bookle - A Flask Implementation
This is a Flask based implementation of a customisable cook book. Registered users can
add, edit, view and browse recipes and can also add/remove favourites. New categories
can be requested and either approved or rejected by an administrator.

# Installation (Heroku)
```
git clone https://github.com/julian-garcia/cookbook.git
source bin/activate
heroku login
heroku apps:create my-app-name
git push -u heroku master
heroku ps:scale web=1  (scale dyno quantity up or down)
```

# Languages/Framework
- Flask
- Python 3.6.5
- Jinja 2.10
- HTML, css, scss
- Materialize 1.0.0-rc.2
- jQuery 3.3.1
- d3 v5
- dc 3.0.4
- crossfilter 1.3.12

## Other
- Fontawesome 5.1.0
- Google Fonts (Material icons, Courgette, Overpass, Pacifico)
- See requirements.txt for all Flask extensions

# Design
A rough wireframe was generated using draw.io. The wireframes can be viewed by
opening mockup.xml via the draw.io website. The colour scheme was defined using
coolor.co, details of the selected scheme are in palette.pdf
