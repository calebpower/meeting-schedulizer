from django.urls import path

from . import views

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    path('create_todo', views.CreateTodoItem.as_view(), name='create-todo')
]