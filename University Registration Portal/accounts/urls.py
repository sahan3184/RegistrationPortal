from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view, post_login_redirect

urlpatterns = [
    path('login/',  auth_views.LoginView.as_view(template_name='accounts/login.html'), name='admin-login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', signup_view, name='signup'),
    path('redirect/', post_login_redirect, name='post-login-redirect'),
]
