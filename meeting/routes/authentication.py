from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.contrib.auth.models import User

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
        existing_user = User.objects.filter(username=username).count()
        username_duplicate = False if existing_user == 0 else True
        
        if username is None:
            errors['usernameEmpty'] = True
        if username_duplicate is True:
            errors['usernameDuplicate'] = True
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
    
class ProfilePage(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')
        logged_in_user = request.user
        username = logged_in_user.username
        display_name = logged_in_user.profile.display_name
        org = logged_in_user.profile.org
        return render(request, 'profile_page.html', { 'username': username, 'displayName': display_name, 'org': org, 'is_no_errors': True, 'get_load': True })

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('LoginProcess')

        username = request.POST.get('inputUsername') if request.POST.get('inputUsername') else None
        display_name = request.POST.get('inputDisplayName') if request.POST.get('inputDisplayName') else None
        org = request.POST.get('inputOrg') if request.POST.get('inputOrg') else None
        errors = dict()

        if org is None:
            errors['orgEmpty'] = True
        elif org.isspace() is True:
            errors['orgEmpty'] = True

        if display_name is None:
            errors['displayNameEmpty'] = True
        elif display_name.isspace() is True:
            errors['displayNameEmpty'] = True

        if username is None:
            errors['usernameEmpty'] = True
        elif username.isspace() is True:
            errors['usernameEmpty'] = True

        existing_user = User.objects.filter(username=username).count()
        username_duplicate = False if existing_user == 0 else True
        
        if username_duplicate is True:
            found_user = User.objects.filter(username=username)[0]
            if found_user.username != request.user.username:
                errors['usernameDuplicate'] = True

        is_no_errors = not bool(errors)
        if is_no_errors:
            editing_user = User.objects.get(username=request.user.username)
            editing_user.username = username
            editing_user.profile.display_name = display_name
            editing_user.profile.org = org
            editing_user.save()
        else:
            logged_in_user = request.user
            username = logged_in_user.username
            display_name = logged_in_user.profile.display_name
            org = logged_in_user.profile.org
        return render(request, 'profile_page.html', {'username': username, 'displayName': display_name, 'org': org, 'errors': errors, 'is_no_errors': is_no_errors, 'get_load': False })

class LogoutPage(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return redirect('LoginProcess')
            
  
