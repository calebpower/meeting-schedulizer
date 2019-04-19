from django.db import models

# Create your models here.

class TodoItem(models.Model):

    

    # DB fields
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=280, null=True)
    date_created = models.DateTimeField('date created')
    date_due = models.DateTimeField('date due')
    date_doing = models.DateTimeField('date doing', null=True)
    priority_level = models.IntegerField(default=0)
    catagory = models.IntegerField(default=0)
    is_done = models.BooleanField(default=False)
    showAlways = models.BooleanField(default=False)

    # model methods
    