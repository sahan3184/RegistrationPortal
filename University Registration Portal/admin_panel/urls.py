from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="admin-dashboard"),

      # Authentication
    path("login/", auth_views.LoginView.as_view(template_name="adminPanel/login.html"), name="admin-login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="admin-login"), name="logout"),

    # Departments
    path("departments/", views.departments_view, name="departments"),
    path("departments/edit/<int:pk>/", views.department_edit, name="department-edit"),
    path("departments/delete/<int:pk>/", views.department_delete, name="department-delete"),

    # Courses
    path("courses/", views.courses_view, name="courses"),
    path("courses/edit/<int:pk>/", views.course_edit, name="course-edit"),
    path("courses/delete/<int:pk>/", views.course_delete, name="course-delete"),

    # Faculty
    path("faculty/", views.faculty_view, name="faculty"),
    path("faculty/edit/<int:pk>/", views.faculty_edit, name="faculty-edit"),
    path("faculty/remove/<int:pk>/", views.faculty_remove, name="remove-faculty"),
]
