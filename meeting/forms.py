from django import forms
from meeting.models import Meeting

class MeetingForm(forms.ModelForm):
    date = forms.CharField()
    location = forms.CharField()
    optional_members = forms.CharField()
    description = forms.CharField()

    class Meta:
        model = Meeting
        fields = ('date', 'location', 'optional_members', 'description',)
