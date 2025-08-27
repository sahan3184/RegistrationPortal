from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('faculty/', include('faculty.urls')),
    path('admin_panel/', include('admin_panel.urls'))
    
]
