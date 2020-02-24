from django.contrib import admin

from .models import Profile
from .models import Project
from .models import Member

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Member)
