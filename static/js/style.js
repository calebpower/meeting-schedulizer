$(document).ready(function() {

  // do this only for the projects page
  if($('#project-pane').length && $('#active-pane').length) {
    
    Split(["#project-pane","#active-pane"], {
      elementStyle: function (dimension, size, gutterSize) { 
        $(window).trigger('resize'); // Optional
        $("#projects").height($(window).height()
            - $("#titular-nav").height()
            - parseFloat($("#titular-nav").css('padding-top'))
            - parseFloat($("#titular-nav").css('padding-bottom')));
        return { 'flex-basis': 'calc(' + size + '% - ' + gutterSize + 'px)' }
      },
      gutterStyle: function (dimension, gutterSize) { return {'flex-basis':  gutterSize + 'px'} },
      sizes: [20,60,20],
      minSize: 200,
      gutterSize: 0, // meh
      cursor: 'col-resize'
    });

    $('#create-project-btn').on('click', function() {
      window.location = '/meeting/projects/create';
    });
    
    $('#edit-project-btn').on('click', function() {
      window.location = window.location + '/edit';
    });
    
    $('.project-card').click(function() {
      window.location = '/meeting/projects/' + $(this).attr('project');
    });

  }

});