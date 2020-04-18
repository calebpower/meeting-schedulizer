from django.contrib import admin

from .models import Profile
from .models import Project
from .models import Member
from .models import TimeAvailability
from .models import Meeting
from .models import Notification

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Member)
admin.site.register(TimeAvailability)
admin.site.register(Meeting)
admin.site.register(Notification)
