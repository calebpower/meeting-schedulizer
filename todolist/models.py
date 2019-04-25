from django.db import models

# Create your models here.

class TodoItem(models.Model):

    # The name of the todo item
    title = models.CharField(max_length=42)
    # A description of the todo item
    description = models.CharField(max_length=280, null=True)
    # The date the todo item was created (date.now)
    date_created = models.DateField('date created')
    # The date the todo item MUST be completed by
    date_due = models.DateField('date due')
    # The date the user plans on completing the todo item
    date_doing = models.DateField('date doing', null=True)
    # The priority level (defined by constants, 1-4)
    priority_level = models.IntegerField(default=0)
    # The catagory of the todo item (defined by constants, 1-4)
    catagory = models.IntegerField(default=0)
    # If the todo item is marked as complete
    is_done = models.BooleanField(default=False)
    # If the todo item should always be shown regardless of dates
    show_always = models.BooleanField(default=False)

    # model methods
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'dateCreated': self.date_created,
            'dateDue': self.date_due,
            'dateDoing': self.date_doing,
            'priorityLevel': self.priority_level,
            'catagory': self.catagory,
            'isDone': self.is_done,
            'showAlways': self.show_always,
        }
    