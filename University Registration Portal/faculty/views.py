# faculty/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from admin_panel.models import Faculty, Department, Course
from students.models import Student, Enrollment
import re

# Faculty login view
def faculty_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if it's a faculty email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@diu\.edu\.bd$', email):
            messages.error(request, "Please use your faculty email (@diu.edu.bd)")
            return redirect('faculty-login')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Check if user is associated with a faculty member
            try:
                faculty = Faculty.objects.get(user=user)
                login(request, user)
                return redirect('faculty-dashboard')
            except Faculty.DoesNotExist:
                messages.error(request, "No faculty profile found for this account")
        else:
            messages.error(request, "Invalid credentials")
    
    return render(request, 'faculty/login.html')

# Faculty logout view
def faculty_logout(request):
    logout(request)
    return redirect('faculty-login')

# Faculty dashboard view
@login_required
def dashboard(request):
    try:
        faculty = Faculty.objects.get(user=request.user)
        
        # Get advisees count
        advisees_count = Student.objects.filter(advisor=faculty).count()
        
        # Get pending approvals count
        current_semester = "Spring 2025"  # You might want to make this dynamic
        pending_count = Enrollment.objects.filter(
            student__advisor=faculty,
            semester=current_semester,
            status='pending'
        ).count()
        
        # Get approved count for this semester
        approved_count = Enrollment.objects.filter(
            student__advisor=faculty,
            semester=current_semester,
            status='approved'
        ).count()
        
        context = {
            'faculty': faculty,
            'advisees_count': advisees_count,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'active': 'dashboard'
        }
        return render(request, 'faculty/dashboard.html', context)
    
    except Faculty.DoesNotExist:
        messages.error(request, "No faculty profile found")
        return redirect('faculty-login')

# Student list view
@login_required
def student_list(request):
    try:
        faculty = Faculty.objects.get(user=request.user)
        students = Student.objects.filter(advisor=faculty).order_by('student_id')
        
        context = {
            'faculty': faculty,
            'students': students,
            'active': 'students'
        }
        return render(request, 'faculty/student_list.html', context)
    
    except Faculty.DoesNotExist:
        messages.error(request, "No faculty profile found")
        return redirect('faculty-login')

# Approve registrations view
@login_required
def approve_registration(request):
    try:
        faculty = Faculty.objects.get(user=request.user)
        current_semester = "Spring 2025"  # Make this dynamic
        
        # Get pending enrollments for advisees
        pending_enrollments = Enrollment.objects.filter(
            student__advisor=faculty,
            semester=current_semester,
            status='pending'
        ).select_related('student', 'course')
        
        # Group enrollments by student
        enrollments_by_student = {}
        for enrollment in pending_enrollments:
            student_id = enrollment.student.id
            if student_id not in enrollments_by_student:
                enrollments_by_student[student_id] = {
                    'student': enrollment.student,
                    'enrollments': []
                }
            enrollments_by_student[student_id]['enrollments'].append(enrollment)
        
        if request.method == 'POST':
            # Handle approval/rejection
            enrollment_id = request.POST.get('enrollment_id')
            action = request.POST.get('action')
            
            if enrollment_id and action:
                enrollment = get_object_or_404(Enrollment, id=enrollment_id)
                if action == 'approve':
                    enrollment.status = 'approved'
                    enrollment.save()
                    messages.success(request, f"Approved {enrollment.course.code} for {enrollment.student.full_name}")
                elif action == 'reject':
                    enrollment.status = 'rejected'
                    enrollment.save()
                    messages.success(request, f"Rejected {enrollment.course.code} for {enrollment.student.full_name}")
            
            return redirect('approve-registrations')
        
        context = {
            'faculty': faculty,
            'enrollments_by_student': enrollments_by_student.values(),
            'active': 'approve'
        }
        return render(request, 'faculty/approve_reject.html', context)
    
    except Faculty.DoesNotExist:
        messages.error(request, "No faculty profile found")
        return redirect('faculty-login')