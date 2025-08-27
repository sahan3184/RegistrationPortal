from django.shortcuts import render, redirect, get_object_or_404
from .models import Department, Course, Faculty
from django.contrib.auth.decorators import login_required

# ---- Helper: semester list ----
def make_semesters(year_from=None, year_to=None):
    from datetime import date
    SEASONS = [("Spring", 1), ("Summer", 2), ("Fall", 3), ("Short", 4)]
    y = date.today().year
    year_from = year_from or (y - 1)
    year_to   = year_to   or (y + 1)
    rows = []
    for year in range(year_from, year_to + 1):
        yy = year % 100
        for name, idx in SEASONS:
            code = yy * 10 + idx
            rows.append({"label": f"{name} {year}, {code}"})
    rows.sort(key=lambda r: r["label"], reverse=True)
    return rows

# ---- Dashboard ----
@login_required
def dashboard(request):
    ctx = dict(
        total_departments=Department.objects.count(),
        total_courses=Course.objects.count(),
        total_faculty=Faculty.objects.count(),
        departments=Department.objects.order_by("name"),
        courses=Course.objects.select_related("department").order_by("code"),
        faculty_members=Faculty.objects.select_related("department").order_by("name"),
    )
    return render(request, "adminPanel/dashboard.html", ctx)

# ---- Departments ----
@login_required
def departments_view(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        code = (request.POST.get("code") or "").strip().upper()
        if name and code:
            Department.objects.get_or_create(name=name, code=code)
        return redirect("departments")
    return render(request, "adminPanel/departments.html", {
        "departments": Department.objects.order_by("id")
    })

@login_required
def department_delete(request, pk):
    get_object_or_404(Department, pk=pk).delete()
    return redirect("departments")

@login_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        code = (request.POST.get("code") or "").strip().upper()
        if name and code:
            dept.name = name
            dept.code = code
            dept.save()
        return redirect("departments")
    return render(request, "adminPanel/department_edit.html", {"dept": dept})

# ---- Courses ----
@login_required
def courses_view(request):
    if request.method == "POST":
        code = (request.POST.get("code") or "").strip().upper()
        title = (request.POST.get("title") or "").strip()
        semester_label = (request.POST.get("semester_label") or "").strip()
        dept_id = request.POST.get("department_id")
        credit_raw = request.POST.get("credit", "3")
        try:
            credit = float(credit_raw)
        except ValueError:
            credit = 3.0

        dept = Department.objects.filter(id=dept_id).first() if dept_id else None

        if code and title:
            Course.objects.get_or_create(
                code=code,
                defaults={
                    "title": title,
                    "semester_label": semester_label,
                    "department": dept,
                    "credit": credit,
                }
            )
        return redirect("courses")

    return render(request, "adminPanel/courses.html", {
        "courses": Course.objects.select_related("department").order_by("code"),
        "departments": Department.objects.order_by("name"),
        "semesters": make_semesters(),
    })

@login_required
def course_delete(request, pk):
    get_object_or_404(Course, pk=pk).delete()
    return redirect("courses")

@login_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    departments = Department.objects.order_by("name")
    semesters = make_semesters()
    if request.method == "POST":
        code = (request.POST.get("code") or "").strip().upper()
        title = (request.POST.get("title") or "").strip()
        semester_label = (request.POST.get("semester_label") or "").strip()
        credit_raw = request.POST.get("credit", f"{course.credit}")
        try:
            credit = float(credit_raw)
        except ValueError:
            credit = course.credit
        dept_id = request.POST.get("department_id")
        dept = Department.objects.filter(id=dept_id).first() if dept_id else None

        if code and title:
            course.code = code
            course.title = title
            course.semester_label = semester_label
            course.credit = credit
            course.department = dept
            course.save()
        return redirect("courses")

    return render(request, "adminPanel/course_edit.html", {
        "course": course,
        "departments": departments,
        "semesters": semesters,
    })

# ---- Faculty ----
@login_required
def faculty_view(request):
    if request.method == "POST":
        faculty_id = (request.POST.get("faculty_id") or "").strip()
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        dept_id = request.POST.get("department")
        dept = Department.objects.filter(id=dept_id).first() if dept_id else None

        if faculty_id and name and email:
            Faculty.objects.get_or_create(
                faculty_id=faculty_id,
                defaults={"name": name, "email": email, "department": dept}
            )
        return redirect("faculty")

    return render(request, "adminPanel/faculty.html", {
        "faculties": Faculty.objects.select_related("department").order_by("name"),
        "departments": Department.objects.order_by("name"),
    })

@login_required
def faculty_edit(request, pk):
    fac = get_object_or_404(Faculty, pk=pk)
    departments = Department.objects.order_by("name")
    if request.method == "POST":
        faculty_id = (request.POST.get("faculty_id") or "").strip()
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        dept_id = request.POST.get("department")
        dept = Department.objects.filter(id=dept_id).first() if dept_id else None

        if faculty_id and name and email:
            fac.faculty_id = faculty_id
            fac.name = name
            fac.email = email
            fac.department = dept
            fac.save()
        return redirect("faculty")
    return render(request, "adminPanel/faculty_edit.html", {
        "fac": fac,
        "departments": departments,
    })

@login_required
def faculty_remove(request, pk):
    get_object_or_404(Faculty, pk=pk).delete()
    return redirect("faculty")
