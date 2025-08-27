from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    credit = models.DecimalField(max_digits=3, decimal_places=1, default=3.0)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    semester_label = models.CharField(max_length=50, blank=True)

    def __str__(self):
        d = self.department.code if self.department else "-"
        return f"{self.code} - {self.title} [{d}]"


class Faculty(models.Model):
    faculty_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    
    from django.conf import settings
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        dep = self.department.code if self.department else "-"
        return f"{self.faculty_id} - {self.name} ({dep})"
