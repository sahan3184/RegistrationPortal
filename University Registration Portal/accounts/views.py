# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import CustomUser

def signup_view(request):
    ctx = {"errors": {}}

    if request.method == "POST":
        role  = (request.POST.get("role") or "").strip()
        email = (request.POST.get("email") or "").strip()
        iid   = (request.POST.get("institutional_id") or "").strip()  # Student/Faculty ID
        pwd1  = request.POST.get("password1") or ""
        pwd2  = request.POST.get("password2") or ""

        # 1) basic checks
        if role not in [CustomUser.STUDENT, CustomUser.FACULTY, CustomUser.ADMIN]:
            ctx["errors"]["role"] = "Select a valid role."
        if role != CustomUser.ADMIN and not iid:
            ctx["errors"]["institutional_id"] = "Student/Faculty হলে ID আবশ্যক।"
        if pwd1 != pwd2:
            ctx["errors"]["password"] = "Passwords do not match."

        # username পলিসি: আমরা username হিসাবে institutional_id বা email ব্যবহার করব
        if role == CustomUser.ADMIN:
            if not email:
                ctx["errors"]["email"] = "Admin এর জন্য Email প্রয়োজন।"
            username = email or "admin_user"
        else:
            username = iid or email  # Student/Faculty হলে ID-টাই username হিসেবে নেব

        if not ctx["errors"]:
            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email or None,
                    password=pwd1,
                    role=role,
                    institutional_id=iid or None,
                )
            except IntegrityError:
                ctx["errors"]["institutional_id"] = "এই ID আগে থেকেই ব্যবহৃত হচ্ছে।"
            else:
                login(request, user)
                return redirect("post-login-redirect")

        # POST ব্যর্থ হলে ফর্ম ভ্যালুগুলো রিটার্ন করবো
        ctx.update({"role": role, "email": email, "institutional_id": iid})

    return render(request, "accounts/signup.html", ctx)


@login_required
def post_login_redirect(request):
    u = request.user
    if u.role == CustomUser.STUDENT:
        return redirect("student-dashboard")
    elif u.role == CustomUser.FACULTY:
        return redirect("faculty-dashboard")
    elif u.role == CustomUser.ADMIN:
        return redirect("admin-dashboard")
    return redirect("admin-login")
