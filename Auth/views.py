from django.shortcuts import render, redirect
from .form import StudentRegistrationForm, EditProfileWithPasswordForm
from branchDepart.models import Department, Program
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from Audits.models import AuditLog
from project.models import Project
from django.db.models import Count, Q
from django.contrib.auth import update_session_auth_hash
from .form import StudentPasswordChangeForm
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from django.utils import timezone

@login_required
def edit_profile(request):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=f"Visited edit profile page"
    )

    user = request.user

    if request.method == 'POST':
        form = EditProfileWithPasswordForm(request.POST, instance=user)
        if form.is_valid():
            # Update profile fields
            form.save()
            
            # Handle password change
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password1')
            if old_password and new_password:
                if user.check_password(old_password):
                    user.set_password(new_password)
                    user.save()
                    # Keep user logged in after password change
                    update_session_auth_hash(request, user)
                else:
                    form.add_error('old_password', 'Current password is incorrect.')
                    return render(request, 'reg/edit_profile.html', {'form': form})
            
            return redirect('auth:edit_profile')
    else:
        form = EditProfileWithPasswordForm(instance=user)
#success message after updating the profile
        messages.success(request, "Your profile has been updated successfully.")


    return render(request, 'reg/edit_profile.html', {'form': form})

@login_required
def profile(request):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=f"Viewed profile "
    )

    user = request.user  # get the currently logged-in user
    department = getattr(user, 'department', None)
    
    context = {
        'user': user,
        'department': department,
    }
    return render(request, 'reg/profile.html', context)


#rate limit

from datetime import timedelta

MAX_ATTEMPTS = 5
LOCK_TIME = 600  # 10 minutes


def get_lock_key(username):
    return f"login_lock:{username}"


def get_fail_key(username):
    return f"login_fail:{username}"

def is_locked(username):
    lock_until = cache.get(get_lock_key(username))

    if not lock_until:
        return False

    # if lock expired, remove it
    if timezone.now() > lock_until:
        cache.delete(get_lock_key(username))
        return False

    return True

def get_lock_remaining(username):
    lock_until = cache.get(get_lock_key(username))

    if not lock_until:
        return 0

    remaining = (lock_until - timezone.now()).total_seconds()

    return max(int(remaining), 0)

def add_failed_attempt(username):
    key = get_fail_key(username)
    attempts = cache.get(key, 0) + 1

    cache.set(key, attempts, timeout=LOCK_TIME)

    if attempts >= MAX_ATTEMPTS:
        lock_until = timezone.now() + timedelta(seconds=LOCK_TIME)

        cache.set(get_lock_key(username), lock_until, timeout=LOCK_TIME)
        cache.delete(key)

def reset_attempts(username):
    cache.delete(get_fail_key(username))
    cache.delete(get_lock_key(username))


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 🔴 CHECK LOCK FIRST
        if is_locked(username):
            remaining = get_lock_remaining(username)

            
            return render(request, 'reg/login.html', {
                "locked": True,
                "remaining": remaining
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # ✅ reset failures on success
            reset_attempts(username)

            AuditLog.objects.create(
                user=user,
                action=f"User '{username}' logged in successfully"
            )

            if user.is_superuser:
                return redirect('/admin/')
            elif hasattr(user, 'role') and user.role == 'student':
                return redirect('auth:dashboard')
            elif hasattr(user, 'role') and user.role == 'supervisor':
                response = redirect('supervisor:sdashboard')
                if user.is_staff:
                    request.session['can_access_admin'] = True
                return response
            elif hasattr(user, 'role') and user.role == 'admin':
                return redirect('/admin/')
            else:
                messages.error(request, "User role not assigned")
                return redirect('login')

        else:
            # ❌ FAILED LOGIN → increment counter
            add_failed_attempt(username)

            messages.error(request, "Invalid username or password")

            AuditLog.objects.create(
                user=None,
                action=f"Failed login attempt for username '{username}'"
            )

            return render(request, 'reg/login.html')

    return render(request, 'reg/login.html')
def landing_page(request):
    return render(request, "home.html")


  

@login_required
def student_dashboard(request):
    user = request.user
    department = user.department

    programs = Program.objects.filter(department=department)
    projects = Project.objects.filter(students=user)

    # ✅ annotate unread feedback count
    projects = projects.annotate(
        unread_feedback=Count(
            'feedbacks',
            filter=Q(feedbacks__is_read=False)
        )
    )

    context = {
        'programs': programs,
        'department': department,
        'projects': projects,
        'projects_count': projects.count(),
    }

    return render(request, 'reg/student_dashboard.html', context)
def student_register(request):
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # Create user object but don't save yet
            user = form.save(commit=False)
            
            # Set role explicitly
            user.role = 'student'
            
            # Save the user to database
            user.save()
                  # Log the registration action
            AuditLog.objects.create(
                user=user,  # the newly registered student
                action=f"Student '{user.username}' registered successfully"
            )
        
            
            return redirect('auth:login')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'reg/student_register.html', {'form': form})


def load_departments(request):
    branch_id = request.GET.get('branch')
    departments = Department.objects.filter(branch_id=branch_id).values('id', 'name')
    return JsonResponse(list(departments), safe=False)
# Auth/views.py


@login_required
def change_password(request):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=f"Visited change password page"
    )

    if request.method == 'POST':
        form = StudentPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  # Saves new password
            update_session_auth_hash(request, user)  # Keeps user logged in
            messages.success(request, "Your password has been changed successfully.")
            return redirect('auth:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentPasswordChangeForm(user=request.user)
    return render(request, 'reg/change_password.html', {'form': form})

from django.shortcuts import redirect

def log(request):
    if request.user.is_authenticated:
        # Log the logout action manually
        AuditLog.objects.create(
            user=request.user,
            action=f"User '{request.user.username}' logged out"
        )
    
    # Log the user out
    logout(request)

    return redirect('/')  # redirects to home/login page


from django.shortcuts import render, redirect
from django.contrib import messages
from .form import PasswordResetCustomForm

from django.shortcuts import render, redirect
from django.contrib import messages

@ratelimit(key='post:email', rate='5/m', block=True)
def custom_password_reset(request):
    if request.method == "POST":
        form = PasswordResetCustomForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            new_password = form.cleaned_data["password"]

            user.set_password(new_password)
            user.save()

            messages.success(request, "Password reset successful.")
            return redirect("login")
    else:
        form = PasswordResetCustomForm()

    return render(request, "accounts/password_reset.html", {"form": form})