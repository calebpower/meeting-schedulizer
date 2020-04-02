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

//TODO
function onDelete(meeting) {

    title = meeting.title
    location = meeting.location
    start_date = meeting.start_date
    end_date = meeting.end_date
    project = meeting.project 

    var toDelete = Meeting.objects.filter(title=title, location=location, start_date=start_date, end_date=end_date, project=project).delete();
    $('#delete-meeting').meeting;
}