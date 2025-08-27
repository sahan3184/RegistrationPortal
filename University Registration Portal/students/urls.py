from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='student-dashboard'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('registration/', views.registration, name='registration'),
    path('result/', views.result, name='result'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    
    

]
