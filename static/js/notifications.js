var getCookie = function(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');
    for(let i = 0; i < cookies.length; i++) {
      let  cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if(cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
var csrftoken = getCookie('csrftoken');

var notify = function(user, message, link) {
  if(!message) {
    console.log('Notification error: message must be specified.');
  }
  
  let payload = {
    'message': message,
    'csrfmiddlewaretoken': getCookie('csrftoken')
  };
  
  if(user) {
    payload['user'] = user;
    payload['action'] = 'notify';
  } else {
    payload['action'] = 'broadcast';
  }
  
  if(link) {
    payload['link'] = link;
  }
  
  $.post("/meeting/notifications", payload, function(data, status) {
    console.log(data);
    let response = JSON.parse(data.replace(/&#x27;/gi, '"'));
    $.amaran({
      'message': `(${response.status}) ${response.message}`
    });
  });
}

var pollReady = true;

$(document).ready(function() {
  setInterval(function() {
    if(pollReady) {
      pollReady = false;
      
      $.get("/meeting/notifications", function(data, status) {
        let response = JSON.parse(data.replace(/&quot;/gi, '"'));
        
        if(response.status && response.status == 'error') {
          console.log("Notification error: " + response.message);
        } else if(response.status && response.status == 'ok') {
          
          for(let i = 0; i < response.notifications.length; i++) {
            let payload = {
              'message': response.notifications[i].message
            };
            
            if(response.notifications[i].link) {
              if(response.notifications[i].link.charAt(0) == '/') {
                payload['onClick'] = function() {
                  window.location.pathname = response.notifications[i].link
                };
              } else {
                payload['onClick'] = function() {
                  window.location = response.notifications[i].link
                };
              }
            }
            
            $.amaran(payload);
          }
          
        } else {
          console.log("Notification error: unspecified");
        }
        
        if(status == 'success') pollReady = true;
      });
    }
  }, 5000);  
});
