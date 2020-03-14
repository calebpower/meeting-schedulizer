from django.shortcuts import render
from django.views.generic import View

class Voting(View):


    MEETING_DURATION = 1
    avaliaveTimeSlots = []
    users = ['Tom']

    def post(self, request,):
        self.users.append(request.POST.get('Name'))
        print("Add_User is called")
        # self.users.append(username)
        context = {
            'users':self.users,
        }
        return render(request, 'voting/index.html', context)
    
    def get(self, request):

        context = {
            'users':self.users,
        }
        return render(request, 'voting/index.html', context)
