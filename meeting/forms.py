from django import forms
from meeting.models import Meeting

class MeetingForm(forms.ModelForm):
    title = forms.CharField()
    location = forms.CharField()
    optional_members = forms.CharField()
    description = forms.CharField()
    start_date = forms.DateField()
    end_date = forms.DateField()

    class Meta:
        model = Meeting
        fields = ('title', 'location', 'optional_members', 'description','start_date', 'end_date')
