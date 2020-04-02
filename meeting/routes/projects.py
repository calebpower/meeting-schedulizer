from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.generic import View
from meeting.views import pull_projects
from meeting.views import pull_profile

from .. import models

''' Render the default projects page '''
def projects(request):
    if not request.user.is_authenticated:
            return redirect('LoginProcess')
    app_url = request.path
    projects = pull_projects(pull_profile(request.user))
    return render(request, 'projects/active_pane/no_selection.html', {'app_url': app_url, 'projects': projects})

class ProjectCreationProcess(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
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
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        app_url = request.path
        projects = pull_projects(pull_profile(request.user))
        return render(request, 'projects/active_pane/create_project.html', {'app_url': app_url, 'projects': projects})
            
''' Render the "edit project" form '''
class ProjectModificationProcess(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
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
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
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
        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        project_key = kwargs['project_key']
        project = models.Project.objects.get(pk=project_key)
        
        if request.POST.get('action') == 'delete':
            print("project -> yeet")
            try:
                project.delete()
            except Exception as e:
                print(e)
            
            return redirect("../projects")
        elif request.POST.get('action') == 'remove':
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
            except Exception as e:
                print(e)
                
        return redirect('../projects')
        
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        app_url = request.path
        profile = pull_profile(request.user)
        projects = pull_projects(profile)
        
        project = None
        team = []
        potential_yoinks = []
        meetings = [] # depends on Courtney
        role = -1
        
        try:
            project = models.Project.objects.get(pk=kwargs['project_key'])
            
            members = models.Member.objects.filter(project=project)
            for member in members:
                team.append(member)
                if member.user == profile:
                    role = member.role
                    
            profiles = models.Profile.objects.all()
            for p in profiles:
                exists = False
                for t in team:
                    if p.user.get_username() == t.user.user.get_username():
                        exists = True
                if not exists:
                    potential_yoinks.append(p.user.get_username())
                    
            mtgs = models.Meeting.objects.filter(project=project)
            for mtg in mtgs:
                meetings.append(mtg)
                
        except Exception as e:
            print(e)
            
        return render(request, 'projects/active_pane/view_project.html', {'app_url': app_url, 'projects': projects, 'project': project, 'team': team, 'meetings': meetings, 'role': role, 'potential_yoinks': potential_yoinks})
