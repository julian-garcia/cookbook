# Cookle Bookle
This is a **Flask** based implementation of a customisable cook book. Pages are rendered using **Python** based views, linking backend data (a **mongoDB** database housed by [mlab](https://mlab.com)) to html templates rendered by the browser. A working demo has been deployed via Heroku at this URL: [cookle-bookle.herokuapp.com](https://cookle-bookle.herokuapp.com)

## Features
- Registered users can:
  - add, edit, view and browse recipes
  - add/remove favourites
  - request new categories
- Requested categories can be approved/rejected by an administrator
- Home page visualisation of the 5 most favourited recipies

## Design
A rough wireframe was generated using draw.io. The wireframes can be viewed by
opening [mockup.xml](resources/mockup.xml) via the draw.io website. The colour scheme was defined using
coolor.co, details of the selected scheme are in [palette.pdf](resources/palette.pdf)

## Installation (Heroku)
```
git clone https://github.com/julian-garcia/cookbook.git
source bin/activate
heroku login
heroku apps:create my-app-name
git push -u heroku master
heroku ps:scale web=1  (scale dyno quantity up or down)
```

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

## Credits
### Media
Images retrieved from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page) - these are freely reusable images
