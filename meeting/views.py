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
    unique_results = [next(rows) for (key, rows) in groupby(all_meetings, key=lambda obj: obj.id)]

    return unique_results
    
''' Render the home page '''
def index(request):
    app_url = request.path
    return render(request, 'home.html', {'app_url': app_url})
