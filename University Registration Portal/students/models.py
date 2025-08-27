from django.db import models
from django.conf import settings  

class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,     
        on_delete=models.CASCADE,
        related_name="student_profile"
    )
    student_id = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=120)
    department = models.CharField(max_length=120, blank=True)
    batch = models.CharField(max_length=32, blank=True)
    current_semester = models.CharField(max_length=64, blank=True)  # e.g., "Spring 2025"
    is_cleared_for_registration = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"


class Course(models.Model):
    code = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=200)
    credit = models.DecimalField(max_digits=3, decimal_places=1, default=3.0)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    STATUS_CHOICES = (
        ("approved", "Approved"),
        ("pending", "Pending"),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    semester = models.CharField(max_length=64)  # e.g., "Spring 2025"
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")

    class Meta:
        unique_together = ("student", "course", "semester")

    def __str__(self):
        return f"{self.student} -> {self.course} ({self.semester}) [{self.status}]"


class SemesterResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="semester_results")
    semester = models.CharField(max_length=64)  # e.g., "3rd Semester" (তুমিই কাস্টমাইজ করতে পারো)
    gpa = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"{self.student} - {self.semester} (GPA {self.gpa})"


class ResultItem(models.Model):
    result = models.ForeignKey(SemesterResult, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    credit = models.DecimalField(max_digits=3, decimal_places=1)
    grade = models.CharField(max_length=4)        # e.g., A, B+, C
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)  # e.g., 4.00, 3.50
