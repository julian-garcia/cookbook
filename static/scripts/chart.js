// Render horizontal barchart for most popular recipes
var ndx = crossfilter(popular_recipes);
var dim = ndx.dimension(dc.pluck('recipe_title'));
var grp = dim.group().reduceSum(function(d) {
            return d.user_count;
          });

dc.rowChart('#popular-graph')
  .width(null)
  .height(300)
  .dimension(dim)
  .group(grp)
  .x(d3.scaleOrdinal())
  .elasticX(true)
  .margins({top: 0, right: 0, bottom: -1, left: 0})
  .transitionDuration(500);

dc.renderAll();
