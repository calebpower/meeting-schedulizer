from django.shortcuts import render
from itertools import chain, groupby
from . import models



''' Pulls a list of the user's projects '''
def pull_projects(profile):
    projects = {
        models.Member.UserProjectRole.OWNER: [],
        models.Member.UserProjectRole.ACTIVE: [],
        models.Member.UserProjectRole.INVITED: []
    }
    
    if profile is not None:
        try:
            members = models.Member.objects.filter(user=profile)
            for member in members:
                projects[member.role].append(member.project)
        except:
            pass
        
    return projects

''' Pulls a user's profile '''
def pull_profile(user):
    if user.is_authenticated:
        try:
            profile = models.Profile.objects.get(user=user)
            if profile:
                return profile
        except:
            pass
        
    return None

'''
    get_meetings_by_user returns a list of ALL (distinct) meetings
    for ALL projects that the user is a member of.
'''
def get_meetings_by_user(user):
    profile = pull_profile(user)
    projects = pull_projects(profile)
    meetings = []
    
    members = models.Member.objects.filter(user=profile)
    
    for member in members:
        if member.role != models.Member.UserProjectRole.INVITED:
            for project in projects[member.role]:
                project_meetings = models.Meeting.objects.filter(project_id=project.id)
                meetings.append(project_meetings)

    all_meetings = list(chain(*meetings))

    # WTF? This was working before but now it's not!
    # Screw it, I'm resorting to a naive double for loop for this.
    # unique_meetings = [next(rows) for (key, rows) in groupby(all_meetings, key=lambda obj: obj.id)]

    unique_meetings = []
    for meeting in all_meetings:
        notfound = True
        for unique_meeting in unique_meetings:
            if meeting.id == unique_meeting.id:
                notfound = False
                break
        if notfound:
            unique_meetings.append(meeting)

    return unique_meetings
    
''' Render the home page '''
def index(request):
    json_data = models.MeetingTime.objects.all();
    meetings_json = "["
    for datum in json_data:
        meetings_json += '{"title":"' + str(datum.meeting.description) + '", "start":"' + str(
            datum.start_time) + '","end":"'
        meetings_json += str(datum.end_time);
        meetings_json += '"},';
    if len(meetings_json) > 1:
        meetings_json = meetings_json[:-1]
    meetings_json += ']';
    app_url = request.path
    return render(request, 'home.html', {'app_url': app_url, 'meetings_json': meetings_json})
