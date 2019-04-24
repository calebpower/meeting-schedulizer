from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View

# Create your views here.

# Render the home page
def index(request):
    app_url = request.path
    return render(request, 'home.html', {'app_url': app_url})

# Handle creating a todo item
class CreateTodoItem(View):
    def post(self, request, *args, **kwargs):

        # Print post request items for temporary test
        # TODO save this data into DB
        print(request.POST.get('todoTitle'))
        print(request.POST.get('todoPriorityLevel'))
        print(request.POST.get('todoDateDue'))
        print(request.POST.get('todoDateDoing'))
        print(request.POST.get('todoCatagory'))
        print(request.POST.get('todoMessage'))
        return redirect('index')