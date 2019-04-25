from django.urls import path

from . import views

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    path('create_todo', views.CreateTodoItem.as_view(), name='create-todo'),
    path('get_todo/day', views.CreateTodoItem.as_view(), name='get-todo-day'),
    path('get_todo/week', views.CreateTodoItem.as_view(), name='get-todo-week'),
    path('get_todo/month', views.CreateTodoItem.as_view(), name='get-todo-month'),
]