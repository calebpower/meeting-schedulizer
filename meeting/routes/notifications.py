from django.shortcuts import render
from django.views.generic import View
from meeting.views import pull_profile
from .. import models
import json

def notification_demo(request):
    profiles = models.Profile.objects.all()
    users = []
    
    for profile in profiles:
        user = {}
        user['username'] = profile.user.get_username()
        user['id'] = profile.user.pk
        users.append(user)
    
    return render(request, 'notification_demo.html', {'users': users})

class NotificationProcess(View):
    def post(self, request, *args, **kwargs):
        response = {}
        
        if not request.user.is_authenticated:
            response['status'] = 'error'
            response['message'] = 'user not authenticated'
            
        else:
        
            if not request.POST.get('action'):
                response['status'] = 'error'
                response['message'] = 'action not specified'
            
            elif request.POST.get('action') == 'broadcast':
                
                if not request.POST.get('message'):
                    response['status'] = 'error'
                    response['message'] = 'message not specified'
                    
                else:
                    profiles = models.Profile.objects.all()
                    
                    if request.POST.get('link'):
                        for profile in profiles:
                            models.Notification.objects.create(user=profile, message=request.POST.get('message'), link=request.POST.get('link'))
                            
                    else:
                        for profile in profiles:
                            models.Notification.objects.create(user=profile, message=request.POST.get('message'))
                
                response['status'] = 'ok'
                response['message'] = 'notification broadcasted to all users'
                
            elif request.POST.get('action') == 'notify':
                
                if not request.POST.get('message'):
                    response['status'] = 'error'
                    response['message'] = 'message not specified'
                
                elif not request.POST.get('user'):
                    response['status'] = 'error'
                    response['message'] = 'user not specified'
                    
                else:
                    user = None
                    
                    try:
                        user = models.User.objects.get(pk=request.POST.get('user'))
                    except:
                        pass
                    
                    if not user:
                        response['status'] = 'error'
                        response['message'] = 'user not found'
                    
                    else:
                        profile = pull_profile(user)
                        
                        if request.POST.get('link'):
                            models.Notification.objects.create(user=profile, message=request.POST.get('message'), link=request.POST.get('link'))
                        else:
                            models.Notification.objects.create(user=profile, message=request.POST.get('message'))
                    
                        response['status'] = 'ok'
                        response['message'] = 'message sent to user ' + user.get_username()
                
            else:
                response['status'] = 'error'
                response['message'] = 'action not recognized'
        
        return render(request, 'notifications.html', {'response': response})
    
    def get(self, request, *args, **kwargs):
        response = {}
        
        if not request.user.is_authenticated:
            response['status'] = 'error'
            response['message'] = 'user not authenticated'
            
        else:
            profile = pull_profile(request.user)
            
            try:
                notifications = models.Notification.objects.filter(user=profile)
                response['notifications'] = []
                
                for notification in notifications:
                    obj = {}
                    obj['message'] = notification.message
                    obj['link'] = notification.link
                    response['notifications'].append(obj)
                    notification.delete()
                    
                response['status'] = 'ok'
                response['message'] = 'successfully retrieved message(s)'
            
            except Exception as e:
                print(e)
                if response['notifications'] is not None:
                    response.pop(notifications)
                response['status'] = 'error'
                response['message'] = 'exception thrown while retrieving notifications'
        
        return render(request, 'notifications.html', {'response': json.dumps(response)})
