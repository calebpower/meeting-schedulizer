from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.models import User

from . import models
import datetime

# Render the home page
def index(request):
    app_url = request.path
    return render(request, 'home.html', {'app_url': app_url})

# Render the projects page
def projects(request):
    app_url = request.path
    return render(request, 'projects.html', {'app_url': app_url})

class LoginProcess(View):
    def post(self, request, *args, **kwargs):
        # collect the user's information to log them in
        username = request.POST.get('inputUsername') if request.POST.get('inputUsername') else None
        password = request.POST.get('inputPassword') if request.POST.get('inputPassword') else None
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        app_url = request.path
        return render(request, 'login.html', {'app_url': app_url, 'errors': True})
    
    def get(self, request, *args, **kwargs):
        app_url = request.path
        return render(request, 'login.html', {'app_url': app_url})

class RegisterProcess(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('inputUsername') if request.POST.get('inputUsername') else None
        password = request.POST.get('inputPassword') if request.POST.get('inputPassword') else None
        confirm_password = request.POST.get('inputConfirmPassword') if request.POST.get('inputConfirmPassword') else None
        display_name = request.POST.get('inputDisplayName') if request.POST.get('inputDisplayName') else None
        errors = dict()
        
        if username is None:
            errors['usernameEmpty'] = True
        if password is None:
            errors['passwordEmpty'] = True
        if confirm_password is None:
            errors['confirmEmpty'] = True
        if display_name is None:
            errors['displayEmpty'] = True
        if password != confirm_password:
            errors['passwordMatch'] = True

        is_no_errors = not bool(errors)

        if is_no_errors:
            u = User.objects.create_user(username, email=None, password=password)
            u.save()
            new_user = User.objects.get(username=u)
            new_user.profile.display_name = display_name
            new_user.save()
            return redirect('LoginProcess')
        else:
            app_url = request.path
            return render(request, 'register.html', {'app_url': app_url, 'errors': errors })

    
    def get(self, request, *args, **kwargs):
        app_url = request.path
        return render(request, 'register.html', {'app_url': app_url})