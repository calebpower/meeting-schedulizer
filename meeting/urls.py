from django.urls import path
from .viewpages import authentication
from .viewpages import availability
from .viewpages import meetings
from .viewpages import notifications
from .viewpages import projects
from .viewpages import voting
from . import views

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    path('availability', availability.availability, name='Availability'),
    path('availability/<int:meeting_id>', availability.Availability.as_view(), name='meeting_availability'),
    path('availability/<int:meeting_id>/delete', availability.AvailabilityDelete.as_view(), name='AvailabilityDelete'),
    path('login', authentication.LoginProcess.as_view(), name="LoginProcess"),
    path('notification_demo', notifications.notification_demo, name='notification_demo'),
    path('notifications', notifications.NotificationProcess.as_view(), name='NotificationProcess'),
    path('profile', authentication.ProfilePage.as_view(), name="ProfilePage"),
    path('projects', projects.projects, name='projects'),
    path('projects/create', projects.ProjectCreationProcess.as_view(), name='ProjectCreationProcess'),
    path('projects/<int:project_key>', projects.ProjectViewProcess.as_view(), name="ProjectViewProcess"),
    path('projects/<int:project_key>/edit', projects.ProjectModificationProcess.as_view(), name="ProjectModificationProcess"),
    path('projects/<int:project_key>/meetings/create', meetings.MeetingView.as_view(), name="MeetingView"),
    path('register', authentication.RegisterProcess.as_view(), name="RegisterProcess"),
    path('voting', voting.Voting.as_view(), name='Voting')
]
