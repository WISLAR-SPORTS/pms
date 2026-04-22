
from .models import SupervisorProfile
from submission.models import Submission

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from project.models import Project
from Auth.form import EditProfileWithPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

# Decorator
def supervisor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'supervisor':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
from django.db.models import Max
@login_required
@supervisor_required
def supervisor_dashboard(request):
    supervisor = SupervisorProfile.objects.get(user=request.user)

    # Step 1: Get latest submission date per student
    latest = Submission.objects.filter(
        project__supervisors=supervisor
    ).values('student').annotate(
        latest_date=Max('submitted_at')
    )

    # Step 2: Get actual submissions matching those dates
    submissions = Submission.objects.filter(
        project__supervisors=supervisor,
        submitted_at__in=[item['latest_date'] for item in latest]
    ).select_related('project', 'student').order_by('-submitted_at')

    # Optional: Mark all seen submissions (after loading for NEW badge)
    # submissions.filter(is_seen=False).update(is_seen=True)

    # Projects assigned to this supervisor
    projects = Project.objects.filter(supervisors=supervisor).distinct()

    context = {
        'username': supervisor.user.username,
        'department': supervisor.department.name if supervisor.department else 'N/A',
        'projects': projects,
        'submissions': submissions,
    }

    return render(request, 'reg/sdashboard.html', context)
from django.http import FileResponse, Http404
from submission.models import Submission

def download_submission(request, submission_id):
    try:
        submission = Submission.objects.get(id=submission_id)
        file_path = submission.file.path  # get the actual file path
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except Submission.DoesNotExist:
        raise Http404("Submission not found")
@login_required
def profile(request):
    user = request.user  # get the currently logged-in user
    department = getattr(user, 'department', None)
    
    context = {
        'user': user,
        'department': department,
    }
    return render(request, 'reg/sprofile.html', context)

@login_required
def edit_profile(request):
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
                    return render(request, 'reg/sedit_profile.html', {'form': form})
            
            return redirect('supervisor:sedit_profile')
    else:
        form = EditProfileWithPasswordForm(instance=user)
#success message after updating the profile
        messages.success(request, "Your profile has been updated successfully.")


    return render(request, 'reg/sedit_profile.html', {'form': form})
