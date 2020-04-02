from django.urls import path
from .routes import authentication
from .routes import availability
from .routes import meetings
from .routes import notifications
from .routes import projects
from .routes import voting
from . import views

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    path('projects', views.projects, name='projects'),
    path('projects/create', views.ProjectCreationProcess.as_view(), name='ProjectCreationProcess'),
    path('projects/<int:project_key>', views.ProjectViewProcess.as_view(), name="ProjectViewProcess"),
    path('projects/<int:project_key>/edit', views.ProjectModificationProcess.as_view(), name="ProjectModificationProcess"),
    path('projects/<int:project_key>/meetings/create', views.MeetingView.as_view(), name="MeetingView"),
    path('login', views.LoginProcess.as_view(), name="LoginProcess"),
    path('register', views.RegisterProcess.as_view(), name="RegisterProcess"),
    path('availability', views.availability, name='Availability'),
    path('availability/<int:meeting_id>', views.Availability.as_view(), name='meeting_availability'),
    path('availability/<int:meeting_id>/delete', views.AvailabilityDelete.as_view(), name='AvailabilityDelete'),
    path('voting_demo', views.VotingDemo.as_view(), name='voting_demo'),
    path('voting', views.voting, name='Voting'),
    path('voting/<int:meeting_id>', views.Voting.as_view(), name='meeting_vote'),
    path('voting/thanks', views.thanks, name='thanks'),
    path('profile', views.ProfilePage.as_view(), name="ProfilePage")
]
