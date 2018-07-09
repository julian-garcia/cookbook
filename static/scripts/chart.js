
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
  .transitionDuration(500)
  .ordinalColors(['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00']);

dc.renderAll();
console.log(popular_recipes);
