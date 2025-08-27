from django.contrib import admin
from .models import Faculty

# Faculty মডেলকে Admin Panel এ রেজিস্টার করা
admin.site.register(Faculty)
