from django.shortcuts import render, redirect
from django.views.generic import View
from meeting.forms import MeetingForm

from .. import models

class MeetingCreation(View):
    template_name = 'project_meetings/create_meeting.html'

    def get(self, request, project_key):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        form = MeetingForm()
        try:
            project = models.Project.objects.get(pk=project_key)
        except:
            pass    
        return render(request, self.template_name, {'form': form, 'project': project})
   

    def post(self, request, project_key):

        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.project = models.Project.objects.get(pk=project_key)
            meeting.state = models.Meeting.VoteState.OPEN
            meeting.save()

            # title = form.cleaned_data['title']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            location = form.cleaned_data['location']
            optional_members = form.cleaned_data['optional_members']
            description = form.cleaned_data['description']
            form = MeetingForm()

            # meeting_id = kwargs.get('meeting_id') if kwargs.get('meeting_id') else None

            return redirect('../../../projects')
        args = {'form': form, 'start_date': start_date, 'end_date': end_date, 'location': location, 'optional_members': optional_members, 'description': description}
        return render(request, self.template_name, args)         

class MeetingView(View): 
    def post(self, request, project_key, meeting_key):
        
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

            return redirect('../../../projects')
        else:
            return render(request, {'app_url': app_url, 'errors': errors})

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        
        form = MeetingForm()
        try:
            meeting_id = kwargs.get('meeting_key') if kwargs.get('meeting_key') else None
            meeting = models.Meeting.objects.get(id=meeting_id) #To Fix
        except:
            pass    

        return render(request, 'project_meetings/edit_meeting.html', {'form': form, 'meeting': meeting})
