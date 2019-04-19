from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Redirect index to the todolist as it is the true homepage
    path('', lambda request: redirect('/todolist/', permanent=True)),
    
    # To Do List App
    path('todolist/', include('todolist.urls')),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)