$( document ).ready(function() {
    // Initialise Materialize JS components
    $(".dropdown-trigger").dropdown();
    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems);
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems);
    var elems = document.querySelectorAll('.tabs');
    var instance = M.Tabs.init(elems);

    // Category -> Subcategory: Dependent drop down list
    var options = $('#subcategory_name').find('option');

    $('#category_name').change(function() {
      // Select subcategories relevant to the selected category only
      var filter_options = options.filter('[cat="' + this.value + '"],[cat=""]');
      $('#subcategory_name').html(filter_options);
      // Re-render all materialize dropdowns
      var elems = document.querySelectorAll('select');
      var instances = M.FormSelect.init(elems);
    });

    // For the edit recipe page we need to auto select the relevant category_name
    // if another subcategory is selected
    $('#subcategory_name').change(function() {
      selected_cat = $(this).find(":selected").attr('cat')
      $('#category_name').val(selected_cat);
      var elems = document.querySelectorAll('select');
      var instances = M.FormSelect.init(elems);
    });

    // Make sure that the svg graphs rendered by d3/dc are responsive to screen size
    function resize_svg() {
        var graph_width = $("#popular-graph").outerWidth() - 20;
        $("#popular-graph").children("svg").width(graph_width);
        dc.renderAll();
    }

    resize_svg();

    $(window).resize(function() {
      resize_svg();
    });
});
