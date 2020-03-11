from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.models import User

from meeting.forms import MeetingForm
from meeting.models import Meeting

from . import models
import datetime

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

def pull_profile(user):
    if user.is_authenticated:
        try:
            profile = models.Profile.objects.get(user=user)
            if profile:
                return profile
        except:
            pass
        
    return None
    
''' Render the home page '''
def index(request):
    app_url = request.path
    return render(request, 'home.html', {'app_url': app_url})

''' Render the default projects page '''
def projects(request):
    app_url = request.path
    projects = pull_projects(pull_profile(request.user))
    return render(request, 'projects/active_pane/no_selection.html', {'app_url': app_url, 'projects': projects})

class ProjectCreationProcess(View):
    def post(self, request, *args, **kwargs):
        # collect the information about the new project
        title = request.POST.get('title') if request.POST.get('title') else None
        description = request.POST.get('description') if request.POST.get('description') else None
        invitees = request.POST.get('invitees') if request.POST.get('invitees') else None
        user = request.user if request.user.is_authenticated else None
        
        if user is None:
            return redirect('LoginProcess')
            
        profile = models.Profile.objects.get(user=user)
        invitee_profiles = set()
        errors = dict()
        if title is None or not title.strip():
            errors['title'] = 'Cannot be empty'
        if description is None or not description.strip():
            errors['description'] = 'Cannot be empty'
        if user is None:
            errors['user'] = 'Cannot be empty'
        if invitees is None or not invitees.strip():
            errors['invited'] = 'Cannot be empty'
        else:
            invitee_usernames = filter(lambda username: username, map(lambda username: username.strip(), invitees.split(',')))
            
            seen_users = set()
            for invitee in invitee_usernames:
                if not invitee and 'invited' not in errors:
                    errors['invited'] = 'Usernames cannot be blank'
                elif not invitee and 'blank' not in errors['invited']:
                    errors['invited'] += '; usernames cannot be blank'
                elif invitee in seen_users and 'invited' not in errors:
                    errors['invited'] = 'Cannot have duplicate username'
                elif invitee in seen_users and 'duplicate' not in errors['invited']:
                    errors['invited'] += '; cannot have duplicate username'
                elif invitee not in seen_users:
                    seen_users.add(invitee)
                    
            for user in seen_users:
                try:
                    u = User.objects.get(username=user)
                    p = models.Profile.objects.get(user=u)
                    invitee_profiles.add(p)
                except User.DoesNotExist:
                    if 'invite' not in errors:
                        errors['invited'] = 'Cannot invite unregistered user'
                    else:
                        errors['invited'] += '; cannot invited unregistered user'
            
        is_no_errors = not bool(errors)
        
        app_url = request.path
        projects = pull_projects(pull_profile(request.user))
        
        if is_no_errors:
            project = models.Project.objects.create(project_name=title, description=description)
            models.Member.objects.create(project=project, user=profile, role=models.Member.UserProjectRole.OWNER)
            for invitee in invitee_profiles:
                models.Member.objects.create(project=project, user=invitee, role=models.Member.UserProjectRole.INVITED)
            return redirect("/meeting/projects/" + str(project.pk))
            # return render(request, 'projects/active_pane/create_project.html', {'app_url': app_url, 'success': 'Successfully created project!', 'projects': projects})
        else:
            return render(request, 'projects/active_pane/create_project.html', {'app_url': app_url, 'errors': errors, 'projects': projects})
    
    def get(self, request, *args, **kwargs):
        app_url = request.path
        projects = pull_projects(pull_profile(request.user))
        return render(request, 'projects/active_pane/create_project.html', {'app_url': app_url, 'projects': projects})
            
''' Render the "edit project" form '''
class ProjectModificationProcess(View):
    def post(self, request, *args, **kwargs):
        title = request.POST.get('title') if request.POST.get('title') else None
        description = request.POST.get('description') if request.POST.get('description') else None
        user = request.user if request.user.is_authenticated else None
        
        if user is None:
            return redirect('LoginProcess')
        
        errors = dict()
        if title is None or not title.strip():
            errors['title'] = 'Cannot be empty'
        if description is None or not description.strip():
            errors['description'] = 'Cannot be empty'
            
        is_no_errors = not bool(errors)
        
        project_key = kwargs['project_key']
        app_url = request.path
        projects = pull_projects(pull_profile(request.user))
        project = None
        
        try:
            project = models.Project.objects.get(pk=project_key)
        except:
            pass
        
        if is_no_errors and project is not None:
            try:
                project.project_name = title
                project.description = description
                project.save()
            except:
                pass
            
            return redirect('../' + str(project_key))
        else:
            return render(request, 'projects/active_pane/edit_project.html', {'app_url': app_url, 'projects': projects, 'project': project, 'errors': errors})
    
    def get(self, request, *args, **kwargs):
        app_url = request.path
        projects = pull_projects(pull_profile(request.user))
        project = None
        
        try:
            project_key = kwargs['project_key']
            project = models.Project.objects.get(pk=project_key)
        except:
            pass
        
        return render(request, 'projects/active_pane/edit_project.html', {'app_url': app_url, 'projects': projects, 'project': project})

class ProjectViewProcess(View):
    def post(self, request, *args, **kwargs):
        #app_url = request.path
        
        project_key = kwargs['project_key']
        project = models.Project.objects.get(pk=project_key)
        
        if request.POST.get('action') == 'remove':
            print("member -> yeet")
            try:
                user = models.User.objects.get(pk=request.POST.get('user'))
                profile = pull_profile(user)
                models.Member.objects.get(user=profile, project=project).delete()
            except Exception as e:
                print(e)
            
            return redirect("./" + str(project_key))
        elif request.POST.get('action') == 'invite':
            print("member -> yoink")
            try:
                user = models.User.objects.get(username=request.POST.get('user'))
                profile = pull_profile(user)
                models.Member.objects.create(project=project, user=profile, role=models.Member.UserProjectRole.INVITED)
            except Exception as e:
                print(e)
                
            return redirect("./" + str(project_key))
        elif request.POST.get('action') == 'accept':
            print("invite -> yoink")
            try:
                user = request.user if request.user.is_authenticated else None
                profile = pull_profile(user)
                models.Member.objects.filter(user=profile, project=project).update(role=models.Member.UserProjectRole.ACTIVE)
            except Exception as e:
                print(e)
                
            return redirect("./" + str(project_key))
        elif request.POST.get('action') == 'reject':
            print("invite -> yeet")
            try:
                user = request.user if request.user.is_authenticated else None
                profile = pull_profile(user)
                models.Member.objects.get(user=profile, project=project).delete()
            except:
                print(e)
                
            return redirect('../projects')
        
        #redirect('.')
        
        #return render(request, 'projects/active_pane/view_project.html', {'app_url': app_url, 'projects': projects, 'project': project, 'team': team, 'meetings': meetings, 'role': role})

    def get(self, request, *args, **kwargs):
        app_url = request.path
        profile = pull_profile(request.user)
        projects = pull_projects(profile)
        
        project = None
        team = []
        meetings = [] # depends on Courtney
        role = -1
        
        try:
            project = models.Project.objects.get(pk=kwargs['project_key'])
            members = models.Member.objects.filter(project=project)
            for member in members:
                team.append(member)
                if member.user == profile:
                    role = member.role
        except Exception as e:
            print(e)
            
        return render(request, 'projects/active_pane/view_project.html', {'app_url': app_url, 'projects': projects, 'project': project, 'team': team, 'meetings': meetings, 'role': role})

class LoginProcess(View):
    def post(self, request, *args, **kwargs):
        # collect the user's information to log them in
        username = request.POST.get('inputUsername') if request.POST.get('inputUsername') else None
        password = request.POST.get('inputPassword') if request.POST.get('inputPassword') else None
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        app_url = request.path
        return render(request, 'login.html', {'app_url': app_url, 'errors': True})
    
    def get(self, request, *args, **kwargs):
        app_url = request.path
        return render(request, 'login.html', {'app_url': app_url})

class RegisterProcess(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('inputUsername') if request.POST.get('inputUsername') else None
        password = request.POST.get('inputPassword') if request.POST.get('inputPassword') else None
        confirm_password = request.POST.get('inputConfirmPassword') if request.POST.get('inputConfirmPassword') else None
        display_name = request.POST.get('inputDisplayName') if request.POST.get('inputDisplayName') else None
        errors = dict()
        
        if username is None:
            errors['usernameEmpty'] = True
        if password is None:
            errors['passwordEmpty'] = True
        if confirm_password is None:
            errors['confirmEmpty'] = True
        if display_name is None:
            errors['displayEmpty'] = True
        if password != confirm_password:
            errors['passwordMatch'] = True

        is_no_errors = not bool(errors)

        if is_no_errors:
            u = User.objects.create_user(username, email=None, password=password)
            u.save()
            new_user = User.objects.get(username=u)
            new_user.profile.display_name = display_name
            new_user.save()
            return redirect('LoginProcess')
        else:
            app_url = request.path
            return render(request, 'register.html', {'app_url': app_url, 'errors': errors })

    
    def get(self, request, *args, **kwargs):
        app_url = request.path
        return render(request, 'register.html', {'app_url': app_url})

''' Availability pages '''
def availability(request):
    # meeting_list = [
    #     type('obj', (object,), {'name' : 'Meeting ONE', 'id' : 1})(),
    #     type('obj', (object,), {'name' : 'Meeting TWO', 'id' : 2})(),
    #     type('obj', (object,), {'name' : 'Meeting THREE', 'id' : 3})()
    # ]
    meeting_list = {
        1: type('obj', (object,), {'name': 'Meeting ONE', 'id': 1, 'start_date': '2020-03-01 06:00:00', 'end_date': '2020-03-07 23:59:59'})(),
        2: type('obj', (object,), {'name': 'Meeting TWO', 'id': 2, 'start_date': '2020-03-08 05:49:01', 'end_date': '2020-03-14 23:59:59'})(),
        3: type('obj', (object,), {'name': 'Meeting THREE', 'id': 3, 'start_date': '2020-03-01 06:00:00', 'end_date': '2020-03-07 23:59:59'})()
    }
    context = {
        'meeting_list': meeting_list,
    }
    return render(request, 'availability/index.html', context)

class Availability(View):
    def get(self, request, meeting_id):

        # models.Meeting.objects.raw('select name, m.id, m.start_date, m.end_date, coalesce(avlb_count, 0)
        #   from meeting_meeting m join (select meeting, count(*) avlb_count from meeting_timeavailability group by meeting) c
        #   on m.id = c.meeting'
        meeting_list = {
            1: type('obj', (object,), {'name': 'Meeting ONE', 'id': 1, 'start_date': '2020-03-01 06:00:00', 'end_date': '2020-03-07 23:59:59', 'avlb_count':2})(),
            2: type('obj', (object,), {'name': 'Meeting TWO', 'id': 2, 'start_date': '2020-03-08 05:49:01', 'end_date': '2020-03-14 23:59:59', 'avlb_count':0})(),
            3: type('obj', (object,), {'name': 'Meeting THREE', 'id': 3, 'start_date': '2020-03-01 06:00:00', 'end_date': '2020-03-07 23:59:59', 'avlb_count':10})()
        }
        active_meeting = meeting_list.get(meeting_id)
        app_url = request.path
        # time_slots = models.TimeAvailability.objects.filter(meeting=meeting_id)
        time_slots = models.TimeAvailability.objects.raw('select * from meeting_timeavailability where meeting = %s', [meeting_id])
        
        context = {
            'active_meeting': active_meeting,
            'meeting_list': meeting_list,
            'app_url': app_url,
            'time_slots': time_slots
        }

        return render(request, 'availability/meeting_availability.html', context)

    def post(self, request, *args, **kwargs):
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        meeting_id = kwargs.get('meeting_id')
        # meetingId = request.POST.get('meeting_id')
        # user = request.user if request.user.is_authenticated else None
        
        # if user is None:
        #     return redirect('LoginProcess')

        models.TimeAvailability.objects.create(start_time=start_time,
                                               end_time=end_time,
                                               meeting=meeting_id)
        
        
        # models.Meeting.objects.raw('select name, m.id, m.start_date, m.end_date, coalesce(avlb_count, 0)
        #   from meeting_meeting m join (select meeting, count(*) avlb_count from meeting_timeavailability group by meeting) c
        #   on m.id = c.meeting'
        meeting_list = {
            1: type('obj', (object,), {'name': 'Meeting ONE', 'id': 1, 'start_date': '2020-03-01 06:00:00', 'end_date': '2020-03-07 23:59:59', 'avlb_count':2})(),
            2: type('obj', (object,), {'name': 'Meeting TWO', 'id': 2, 'start_date': '2020-03-08 05:49:01', 'end_date': '2020-03-14 23:59:59', 'avlb_count':0})(),
            3: type('obj', (object,), {'name': 'Meeting THREE', 'id': 3, 'start_date': '2020-03-01 06:00:00', 'end_date': '2020-03-07 23:59:59', 'avlb_count':10})()
        }
        active_meeting = meeting_list.get(meeting_id)
        app_url = request.path
        time_slots = models.TimeAvailability.objects.filter(meeting=meeting_id)
        
        context = {
            'meeting_list': meeting_list,
            'active_meeting': active_meeting,
            'app_url': app_url,
            'time_slots': time_slots
        }

        return render(request, 'availability/meeting_availability.html', context)


class MeetingView(View):
   template_name = 'create_meeting.html'

   def get(self, request, project_key):
       form = MeetingForm()
       try:
           project = models.Project.objects.get(pk=project_key)
       except:
           pass    
       return render(request, self.template_name, {'form': form, 'project': project})

   def post(self, request, project_key):
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.project = models.Project.objects.get(pk=project_key)
            meeting.save()

            date = form.cleaned_data['date']
            location = form.cleaned_data['location']
            optional_members = form.cleaned_data['optional_members']
            description = form.cleaned_data['description']
            form = MeetingForm()
            return redirect('../../../projects')
        args = {'form': form, 'date': date, 'location': location, 'optional_members': optional_members, 'description': description,}
        return render(request, self.template_name, args)         