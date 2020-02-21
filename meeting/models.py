from django.db import models

''' Denotes a single project. '''
class Project(models.Model):
    project_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)

''' Denotes users related to a project. '''
class ProjectUsers(models.Model):
    class UserProjectRole(models.IntegerChoices):
        INVITED = 0,
        ACTIVE = 1,
        OWNER = 2
    
    user_role = models.IntegerField(choices=UserProjectRole.choices)
    # TODO add variable to denote foreign key to User (waiting on Jacob)
    