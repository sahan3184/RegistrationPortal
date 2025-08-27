from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.faculty_login, name='faculty-login'),
    path('logout/', views.faculty_logout, name='faculty-logout'),
    path('dashboard/', views.dashboard, name='faculty-dashboard'),
    path('student-list/', views.student_list, name='student-list'),
    path('approve-registrations/', views.approve_registration, name='approve-registrations'),
]