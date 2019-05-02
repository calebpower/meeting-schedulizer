$(window, document, undefined).ready(function() {
  
  
    // Show overlay & Open modal
    
    $( ".login-modal-overlay" ).click(function() {
      $(this).fadeOut(200);
    });
    $( ".openb" ).click(function() {
      $(".login-modal-overlay").fadeIn(200);
    });
    $(".login-modal").click(function(event) {
      event.stopPropagation();
    });
  
  });