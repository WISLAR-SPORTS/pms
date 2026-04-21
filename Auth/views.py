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



def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # Log successful login
            AuditLog.objects.create(
                user=user,
                action=f"User '{username}' logged in successfully"
            )

            # Role-based redirection
            if user.is_superuser:
                return redirect('/admin/')  # superusers go to Django admin
            elif hasattr(user, 'role') and user.role == 'student':
                return redirect('auth:dashboard')
            elif hasattr(user, 'role') and user.role == 'supervisor':
                # Redirect to supervisor dashboard first
                response = redirect('supervisor:sdashboard')

                # If supervisor has staff status, allow admin access too
                if user.is_staff:
                    request.session['can_access_admin'] = True
                return response
            elif hasattr(user, 'role') and user.role == 'admin':
                return redirect('/admin/')
            else:
                messages.error(request, "User role not assigned")
                return redirect('login')
        else:
            # Authentication failed
            messages.error(request, "Invalid username or password")
            AuditLog.objects.create(
                user=None,  # unknown user
                action=f"Failed login attempt for username '{username}'"
            )
            return render(request, 'reg/login.html')
    
    # If GET request, just render the login page
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