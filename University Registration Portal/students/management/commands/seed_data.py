from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random
from students.models import Student, Course, Enrollment, SemesterResult, ResultItem

User = get_user_model()

class Command(BaseCommand):
    help = "Generate fake data for Students, Courses, Enrollments, and Results"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # ---------- Create Users & Students ----------
        students = []
        for i in range(50):
            user = User.objects.create_user(
                username=f"student{i+1}",
                email=f"student{i+1}@example.com",
                password="12345"
            )
            student = Student.objects.create(
                user=user,
                student_id=f"STU{i+1:03d}",
                full_name=fake.name(),
                department=random.choice(["CSE", "EEE", "BBA", "LAW"]),
                batch=random.choice(["2021", "2022", "2023", "2024"]),
                current_semester=random.choice(["Spring 2024", "Fall 2024", "Spring 2025"]),
                is_cleared_for_registration=random.choice([True, False])
            )
            students.append(student)

        self.stdout.write(self.style.SUCCESS("✅ Created 50 Students"))

        # ---------- Create Courses ----------
        courses = []
        for i in range(50):
            course = Course.objects.create(
                code=f"CSE{i+100}",
                title=fake.sentence(nb_words=4),
                credit=random.choice([1.0, 2.0, 3.0, 4.0])
            )
            courses.append(course)

        self.stdout.write(self.style.SUCCESS("✅ Created 50 Courses"))

        # ---------- Create Enrollments ----------
        for student in students:
            for course in random.sample(courses, 5):  # প্রতিটি student ৫টা course এ enroll
                Enrollment.objects.create(
                    student=student,
                    course=course,
                    semester=random.choice(["Spring 2024", "Fall 2024", "Spring 2025"]),
                    status=random.choice(["approved", "pending"])
                )

        self.stdout.write(self.style.SUCCESS("✅ Created Enrollments"))

        # ---------- Create Semester Results ----------
        for student in students:
            sem_result = SemesterResult.objects.create(
                student=student,
                semester=random.choice(["1st Semester", "2nd Semester", "3rd Semester"]),
                gpa=round(random.uniform(2.00, 4.00), 2)
            )

            # ---------- Create Result Items ----------
            for course in random.sample(courses, 4):
                grade, gp = random.choice([
                    ("A", 4.00), ("A-", 3.70), ("B+", 3.30), ("B", 3.00),
                    ("C+", 2.30), ("C", 2.00), ("D", 1.00), ("F", 0.00)
                ])
                ResultItem.objects.create(
                    result=sem_result,
                    course=course,
                    credit=course.credit,
                    grade=grade,
                    grade_point=gp
                )

        self.stdout.write(self.style.SUCCESS("🎉 Done! 50 Students, Courses, Enrollments & Results created."))
