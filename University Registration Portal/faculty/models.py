from django.db import models
from django.conf import settings

# -------------------------------
# Department Model
# -------------------------------
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


# -------------------------------
# Faculty Model (faculty app)
# -------------------------------
class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_faculty')  # Added related_name
    faculty_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        dep = self.department.code if self.department else "-"
        return f"{self.faculty_id} - {self.name} ({dep})"

    # Helper methods for Faculty
    def get_assigned_students(self):
        """Get all students from faculty's department"""
        return Student.objects.filter(department=self.department)

    def get_pending_enrollments(self):
        """Get all pending enrollments under faculty's department"""
        return Enrollment.objects.filter(course__department=self.department, status="pending")

    def get_approved_enrollments(self):
        """Get all approved enrollments under faculty's department"""
        return Enrollment.objects.filter(course__department=self.department, status="approved")


# -------------------------------
# Student Model
# -------------------------------
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=120)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    batch = models.CharField(max_length=32, blank=True)
    current_semester = models.CharField(max_length=64, blank=True)
    is_cleared_for_registration = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"


# -------------------------------
# Course Model
# -------------------------------
class Course(models.Model):
    code = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=200)
    credit = models.DecimalField(max_digits=3, decimal_places=1, default=3.0)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="courses")

    def __str__(self):
        return f"{self.code} - {self.title}"


# -------------------------------
# Enrollment Model
# -------------------------------
class Enrollment(models.Model):
    STATUS_CHOICES = (
        ("approved", "Approved"),
        ("pending", "Pending"),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    semester = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")

    class Meta:
        unique_together = ("student", "course", "semester")

    def __str__(self):
        return f"{self.student} -> {self.course} ({self.semester}) [{self.status}]"


# -------------------------------
# Semester Result Model
# -------------------------------
class SemesterResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="semester_results")
    semester = models.CharField(max_length=64)
    gpa = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"{self.student} - {self.semester} (GPA {self.gpa})"


# -------------------------------
# Result Item Model
# -------------------------------
class ResultItem(models.Model):
    result = models.ForeignKey(SemesterResult, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    credit = models.DecimalField(max_digits=3, decimal_places=1)
    grade = models.CharField(max_length=4)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"{self.result.student} -> {self.course.title} (Grade {self.grade})"
