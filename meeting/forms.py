from django import forms
from meeting.models import Meeting

class MeetingForm(forms.ModelForm):
    title = forms.CharField()
    start_date = forms.DateField()
    end_date = forms.DateField()
    location = forms.CharField()
    optional_members = forms.CharField()
    description = forms.CharField()

    class Meta:
        model = Meeting
        fields = ('title','start_date', 'end_date', 'location', 'optional_members', 'description',)
