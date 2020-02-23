from django.urls import path

from . import views

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    path('projects', views.projects, name='projects'),
    path('projects/create', views.projects_create, name='projects_create'),
    path('projects/<int:project_key>', views.projects_view, name='projects_view'),
    path('projects/<int:project_key>/edit', views.projects_edit, name='projects_edit'),
    path('login', views.LoginProcess.as_view(), name="LoginProcess"),
    path('register', views.RegisterProcess.as_view(), name="RegisterProcess")
]