from django.urls import path

from . import views

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
]