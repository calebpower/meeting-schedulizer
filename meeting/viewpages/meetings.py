from django.shortcuts import render, redirect
from django.views.generic import View
from meeting.forms import MeetingForm

from .. import models

class MeetingView(View):
    template_name = 'create_meeting.html'

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
            meeting.save()

            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            location = form.cleaned_data['location']
            optional_members = form.cleaned_data['optional_members']
            description = form.cleaned_data['description']
            form = MeetingForm()
            return redirect('../../../projects')
        args = {'form': form, 'start_date': start_date, 'end_date': end_date, 'location': location, 'optional_members': optional_members, 'description': description}
        return render(request, self.template_name, args)         
