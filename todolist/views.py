from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from . import models
import datetime

# Create your views here.

# Render the home page
def index(request):
    app_url = request.path
    return render(request, 'home.html', {'app_url': app_url})

# Handle creating a todo item
class CreateTodoItem(View):
    def post(self, request, *args, **kwargs):
        
        # collect the info from the post request form
        post_title = request.POST.get('todoTitle') if request.POST.get('todoTitle') else None
        post_priority_level = request.POST.get('todoPriorityLevel') if request.POST.get('todoPriorityLevel') else None
        post_date_due = request.POST.get('todoDateDue') if request.POST.get('todoDateDue') else None
        post_date_doing = request.POST.get('todoDateDoing') if request.POST.get('todoDateDoing') else None
        post_catagory = request.POST.get('todoCatagory') if request.POST.get('todoCatagory') else None
        post_message = request.POST.get('todoMessage') if request.POST.get('todoMessage') else None
        post_always_show = request.POST.get('alwaysShow') if request.POST.get('alwaysShow') else None

        # Save the data from the form into a todo object on the database
        todo_item = models.TodoItem(
            title=post_title,
            description=post_message,
            date_created=datetime.date.today(),
            date_due=post_date_due,
            date_doing=post_date_doing,
            priority_level=post_priority_level,
            catagory=post_catagory,
            is_done=False,
            show_always=True if post_always_show == 'on' else False
        )
        todo_item.save()
        return redirect('index')