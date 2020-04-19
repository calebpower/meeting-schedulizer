//Check Date
function checkDate(){
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0');
    var yyyy = today.getFullYear();
  
    today = yyyy + '-' + mm + '-' + dd;
  
    var selected_start_date = document.getElementById("create-meeting-start_date").value;
    var selected_end_date = document.getElementById("create_meeting-end_date").value;
  
    if (selected_start_date < today) {
        alert("Start date must be in the future");
    }
  
    else if (selected_end_date < selected_start_date) {
        alert("The end date must be after the start date");
    }  
}

//Delete Meeting
$(document).ready(function() {
   if($('#meeting-view-form').length){
       $('#delete-meeting-btn').on('click', function() {
       $("#confirm-remove-meeting-modal").modal();
     });
 
     $('#confirm-meeting-deletion').on('click', function() {
       $("#passback-action").val("delete");
       $("#passback-form").submit();
     });
 
     $('#back-meeting-btn').on('click', function() {
        window.history.back()
      });
 
    }
});


