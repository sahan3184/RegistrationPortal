from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils.timezone import now
from .models import Student, Course, Enrollment, SemesterResult, ResultItem
#signup
from django.contrib.auth import get_user_model
from django.contrib import messages
from students.models import Student
import re

#login
from django.contrib.auth import authenticate, login

def _ensure_student_for_user(user) -> Student:
    """
    Logged-in user এর জন্য Student প্রোফাইল নিশ্চিত করে।
    না থাকলে create করে ফেলে।
    """
    if not user.is_authenticated:
        return None
    # already linked?
    if hasattr(user, "student_profile"):
        return user.student_profile

    # না থাকলে create (সেন্সিবল ডিফল্টসহ)
    full_name = getattr(user, "get_full_name", None)
    full_name = full_name() if callable(full_name) else ""
    if not full_name:
        # username কে fallback হিসেবে নিলাম
        full_name = getattr(user, "username", "Student")

    current_year = now().year
    student = Student.objects.create(
        user=user,
        student_id=f"S-{user.pk:06d}",
        full_name=full_name,
        department="Software Engineering",
        batch="39th",
        current_semester=f"Spring {current_year}",
        is_cleared_for_registration=False,
    )
    return student

@login_required
def dashboard(request):
    student = _ensure_student_for_user(request.user)
    # সেফগার্ড: student না পাওয়া গেলে হালকা fallback (অতি বিরল কেস)
    if student is None:
        return render(request, "students/student_dashboard.html", {
            "student": None,
            "total_credits": 0,
            "completed_credits": 0,
            "pending_count": 0,
            "all_courses": [],
            "completed_items": [],
            "pending_regs": [],
        })

    all_courses = Course.objects.all().order_by("code")

    completed_items = ResultItem.objects.select_related("course", "result")\
        .filter(result__student=student)

    completed_credits = completed_items.aggregate(total=Sum("credit"))["total"] or 0
    total_credits = all_courses.aggregate(total=Sum("credit"))["total"] or 0

    current_sem = student.current_semester or ""
    pending_regs = Enrollment.objects.select_related("course")\
        .filter(student=student, semester=current_sem, status="pending")

    context = {
        "student": student,
        "total_credits": total_credits,
        "completed_credits": completed_credits,
        "pending_count": pending_regs.count(),
        "all_courses": all_courses,
        "completed_items": completed_items,
        "pending_regs": pending_regs,
    }
    return render(request, "students/student_dashboard.html", context)

@login_required
def my_courses(request):
    student = _ensure_student_for_user(request.user)
    if student is None:
        return render(request, "students/my_courses.html", {"student": None, "enrollments": []})

    current_sem = student.current_semester or ""
    enrollments = Enrollment.objects.select_related("course")\
        .filter(student=student, semester=current_sem)\
        .order_by("course__code")

    context = {"student": student, "enrollments": enrollments}
    return render(request, "students/my_courses.html", context)

@login_required
def registration(request):
    student = _ensure_student_for_user(request.user)
    if student is None:
        return render(request, "students/student_registration.html", {
            "student": None,
            "is_cleared": False,
            "available_courses": [],
            "current_enrollments": [],
        })

    current_sem = student.current_semester or ""
    current_enrollments = Enrollment.objects.select_related("course")\
        .filter(student=student, semester=current_sem)

    already_course_ids = current_enrollments.values_list("course_id", flat=True)
    available_courses = Course.objects.exclude(id__in=already_course_ids).order_by("code")

    context = {
        "student": student,
        "is_cleared": bool(student.is_cleared_for_registration),
        "available_courses": available_courses,
        "current_enrollments": current_enrollments,
    }
    return render(request, "students/student_registration.html", context)

@login_required
def result(request):
    student = _ensure_student_for_user(request.user)
    if student is None:
        return render(request, "students/student_result.html", {
            "student": None, "semesters": [], "selected_sem": None,
            "selected_result": None, "items": []
        })

    semesters = list(student.semester_results.values_list("semester", flat=True).order_by("semester"))
    selected_sem = request.GET.get("sem") or (semesters[0] if semesters else None)

    selected_result = None
    items = []
    if selected_sem:
        selected_result = get_object_or_404(SemesterResult, student=student, semester=selected_sem)
        items = ResultItem.objects.select_related("course").filter(result=selected_result)

    context = {
        "student": student,
        "semesters": semesters,
        "selected_sem": selected_sem,
        "selected_result": selected_result,
        "items": items,
    }
    return render(request, "students/student_result.html", context)
# Login and Signup views
User = get_user_model()

def signup(request):
    if request.method == 'POST':
        # Get data from the form
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        student_id = request.POST.get('student_id')  # Get student ID
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        department = request.POST.get('department')
        batch = request.POST.get('batch')

        # Varsity email pattern check (e.g., rakib22205341183@diu.edu.bd)
        email_pattern = r'^[a-zA-Z0-9]+@diu\.edu\.bd$'
        if not re.match(email_pattern, email):
            messages.error(request, "Please enter a valid university email (e.g., rakib22205341183@diu.edu.bd).")
            return redirect('signup')

        # Varsity student ID (using the part before @ in email)
        if not student_id:
            messages.error(request, "Student ID is required.")
            return redirect('signup')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(username=email, email=email, password=password)

        # Create Student profile
        student = Student.objects.create(
            user=user,
            full_name=full_name,
            student_id=student_id,  # Varsity ID as student ID
            department=department,  # Save department
            batch=batch,  # Save batch
            current_semester="Summer 2025",  # Default semester
        )

        messages.success(request, f"Account created for {user.username}!")
        return redirect('login')  # Redirect to login after successful signup

    return render(request, 'students/signup.html')


#login view
def login_view(request):
    if request.method == 'POST':
        login_id = request.POST.get('login_id')  # This will be either student_id or email
        password = request.POST.get('password')

        # Check if the input is email or student_id
        if "@" in login_id:  # If it contains '@', it's an email
            try:
                user = User.objects.get(email=login_id)
            except User.DoesNotExist:
                messages.error(request, "Invalid credentials. Please try again.")
                return redirect('login')
        else:  # Else, it's treated as student_id
            try:
                student = Student.objects.get(student_id=login_id)
                user = student.user  # Get associated user
            except Student.DoesNotExist:
                messages.error(request, "Invalid credentials. Please try again.")
                return redirect('login')

        # Authenticate the user with the found user object
        user = authenticate(request, username=user.username, password=password)
        
        if user is not None:
            login(request, user)  # Successful login
            return redirect('student-dashboard')  # Redirect to student dashboard
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'students/login.html')