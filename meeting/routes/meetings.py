from django.shortcuts import render, redirect
from django.views.generic import View
from meeting.views import pull_profile


from .. import models

class MeetingCreation(View):
    template_name = 'project_meetings/create_meeting.html'

    def get(self, request, project_key):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        team = []

        try:
            project = models.Project.objects.get(pk=project_key)
            
            members = models.Member.objects.filter(project=project)
            for member in members:
                team.append(member)
        except:
            pass   
        return render(request, self.template_name, { 'project': project, 'team': team})
   

    def post(self, request, project_key):
  
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        
        title = request.POST.get('title') if request.POST.get('title') else None
        location = request.POST.get('location') if request.POST.get('location') else None
        optional_members = request.POST._getlist('optional_members')
        description = request.POST.get('description') if request.POST.get('description') else None
        start_date = request.POST.get('start_date') if request.POST.get('start_date') else None
        end_date = request.POST.get('end_date') if request.POST.get('end_date') else None

        if 'required_meeting' in optional_members:
            optional_members = 'required_meeting'
 
        profile = pull_profile(request.user)
        redirect_link = "/meeting/projects/" + str(project_key)
        models.Notification.objects.create(user=profile, message="A new meeting has been created.", link=redirect_link)

        models.Meeting.objects.create(title=title, location=location, optional_members=optional_members, 
                                                description=description, start_date=start_date, end_date=end_date,
                                                project=models.Project.objects.get(pk=project_key))
        
        return redirect("/meeting/projects/" + str(project_key))  
            
              

class MeetingView(View): 
    def post(self, request, project_key, meeting_key):
        
        meeting = models.Meeting.objects.get(id=meeting_key)
        
        if request.POST.get('action') == 'delete':
            try:
                meeting.delete()

                profile = pull_profile(request.user)
                redirect_link = "/meeting/projects/" + str(project_key)
                models.Notification.objects.create(user=profile, message= " Your meeting is deleted!" , link=redirect_link)
           
            except Exception as e:
                print(e)

            return redirect("/meeting/projects/" + str(project_key))

        else:
            title = request.POST.get('title') if request.POST.get('title') else None
            start_date = request.POST.get('start_date') if request.POST.get('start_date') else None
            end_date = request.POST.get('end_date') if request.POST.get('end_date') else None
            location = request.POST.get('location') if request.POST.get('location') else None
            description = request.POST.get('description') if request.POST.get('description') else None

            errors = dict()
            if title is None or not title.strip():
                errors['title'] = 'Cannot be empty'
            if location is None or not location.strip():
                errors['location'] = 'Cannot be empty'        
            if description is None or not description.strip():
                errors['description'] = 'Cannot be empty'    
            
            is_no_errors = not bool(errors)
            app_url = request.path
            meeting = None
        
            try:
                meeting = models.Meeting.objects.get(id=meeting_key)
            except:
                pass
        
            if is_no_errors and meeting is not None:
                try:
                    meeting.title = title
                    meeting.location = location
                    meeting.description = description
                    meeting.start_date = start_date
                    meeting.end_date = end_date

                    meeting.save()

                except:
                    pass

                return redirect("/meeting/projects/" + str(project_key))
            else:
                return render(request, {'app_url': app_url, 'errors': errors})

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        
        user = None
       
        try:
            meeting_id = kwargs.get('meeting_key') if kwargs.get('meeting_key') else None
            meeting = models.Meeting.objects.get(id=meeting_id)


            project = models.Project.objects.get(pk=kwargs.get('project_key'))
            profile = pull_profile(request.user)
            member = models.Member.objects.get(project=project, user=profile)
            
        except:
            pass
        
        if member.role == 2:
            return render(request, 'project_meetings/edit_meeting.html', { 'meeting': meeting, 'user': user})
        else:
            return render(request, 'project_meetings/view_meeting.html', {'meeting': meeting})