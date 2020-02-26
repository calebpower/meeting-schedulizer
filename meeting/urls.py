from django.urls import path

from . import views

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    path('projects', views.projects, name='projects'),
    path('projects/create', views.ProjectCreationProcess.as_view(), name='ProjectCreationProcess'),
    path('projects/<int:project_key>', views.projects_view, name='projects_view'),
    path('projects/<int:project_key>/edit', views.projects_edit, name='projects_edit'),
    path('login', views.LoginProcess.as_view(), name="LoginProcess"),
    path('register', views.RegisterProcess.as_view(), name="RegisterProcess"),
    path('availability', views.availability, name='Availability'),
    path('availability/<int:meeting_id>', views.Availability.as_view(), name='meeting_availability')
]