from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from project.forms import ProjectSubmissionForm
from branchDepart.models import Department, Program
from django.contrib import messages
from django.http import JsonResponse
from Audits.models import AuditLog

def load_departments(request):
    branch_id = request.GET.get('branch_id')
    departments = Department.objects.filter(branch_id=branch_id).values('id', 'name')
    return JsonResponse(list(departments), safe=False)


def load_programs(request):
    department_id = request.GET.get('department_id')
    programs = Program.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse(list(programs), safe=False)
@login_required
def submit_project(request):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action="Visited submit project page"
    )

    if request.user.role != 'student':
        return redirect('home')

    department = getattr(request.user, 'department', None)
    branch = getattr(department, 'branch', None) if department else None

    if not department or not branch:
        messages.error(
            request,
            "Your department or branch is not properly set. Contact the administrator."
        )
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST, user=request.user)

        if form.is_valid():
            project = form.save(commit=False)

            # (optional but recommended)
            project.save()

            project.students.add(request.user)

            AuditLog.objects.create(
                user=request.user,
                action=f"Student '{request.user.username}' has submitted the project successfully"
            )

            messages.success(request, "Project submitted successfully!")
            return redirect('auth:dashboard')

        # ❌ invalid form case
        return render(request, 'project/submit_project.html', {'form': form})

    else:
        form = ProjectSubmissionForm(user=request.user)

    return render(request, 'project/submit_project.html', {'form': form})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Project
from django.contrib.auth.decorators import login_required

@login_required
def supervisor_projects(request):
    if getattr(request.user, "role", None) != "supervisor":
        messages.error(request, "Access denied")
        return redirect("login")

    # Show all projects assigned to this supervisor
    projects = Project.objects.filter(supervisors__user=request.user).distinct()

    return render(request, "project/projects.html", {"projects": projects})


@login_required
def approve_project(request, project_id):
    if getattr(request.user, "role", None) != "supervisor":
        messages.error(request, "Access denied")
        return redirect("login")

    project = get_object_or_404(Project, id=project_id)

    if project.status == "pending":  # Only pending projects can be approved
        project.status = "approved"
        project.save()
        messages.success(request, f"Project '{project.title}' approved!")
    else:
        messages.warning(request, f"Project '{project.title}' cannot be approved from status '{project.status}'")

    return redirect("project:sprojects")


@login_required
def decline_project(request, project_id):
    if getattr(request.user, "role", None) != "supervisor":
        messages.error(request, "Access denied")
        return redirect("login")

    project = get_object_or_404(Project, id=project_id)

    if project.status == "pending":  # Only pending projects can be declined
        project.status = "declined"
        project.save()
        messages.warning(request, f"Project '{project.title}' declined!")
    else:
        messages.info(request, f"Project '{project.title}' cannot be declined from status '{project.status}'")

    return redirect("project:sprojects")

from feedback.forms import FeedbackForm
from submission.models import Submission
@login_required
def give_feedback(request, project_id):
    if getattr(request.user, "role", None) != "supervisor":
        messages.error(request, "Access denied")
        return redirect("login")

    # Get the project
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.project = project   # link to Project
            feedback.supervisor = request.user.supervisorprofile
            feedback.save()
            messages.success(request, "Feedback submitted successfully!")
            return redirect("project:sprojects")
    else:
        form = FeedbackForm()

    return render(request, "reg/give_feedback.html", {"form": form, "project": project})






from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Project
from feedback.models import Feedback
@login_required
def project_feedback_chat(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ensure only related users can access
    if request.user not in project.students.all() and request.user not in project.supervisors.all():
        messages.error(request, "Access denied")
        return redirect("login")

    # ✅ Mark feedback as READ when a student opens the chat
    if request.user in project.students.all():
        Feedback.objects.filter(
            project=project,
            is_read=False
        ).update(is_read=True)

    # ✅ Get all feedback messages
    feedbacks = Feedback.objects.filter(project=project).order_by("created_at")

    # ✅ Get all submissions for this project
    submissions = Submission.objects.filter(project=project).order_by("-submitted_at")

    if request.method == "POST":
        if getattr(request.user, "role", None) != "supervisor":
            messages.error(request, "Only supervisors can send feedback.")
            return redirect("project:feedback_chat", project_id=project.id)
       
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.project = project

            # ✅ attach latest submission
            latest_submission = submissions.first()
            feedback.submission = latest_submission

            feedback.supervisor = request.user.supervisorprofile

            # ✅ ensure new feedback is marked as UNREAD
            feedback.is_read = False

            feedback.save()

            return redirect("project:feedback_chat", project_id=project.id)
    else:
        form = FeedbackForm()

    return render(request, "project/feedback_chat.html", {
        "project": project,
        "feedbacks": feedbacks,
        "form": form,
        "submissions": submissions
    })