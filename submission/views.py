# submissions/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SubmissionForm
from .models import Submission
from Supervisor.models import SupervisorProfile
from django.shortcuts import get_object_or_404
from django.contrib import messages


@login_required
def submit_progress(request):
    if request.user.role != 'student':
        return redirect('home')  # restrict access

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.save()
            return redirect('auth:dashboard')  # after successful submission
    else:
        form = SubmissionForm(user=request.user)

    return render(request, 'submissions/submit_progress.html', {'form': form})

@login_required
def approve_submissions(request):
    if not hasattr(request.user, 'supervisorprofile'):
        return redirect('home')
    
    supervisor = request.user.supervisorprofile
    submissions = Submission.objects.filter(project__supervisors=supervisor, approved=False)
    
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        submission = Submission.objects.get(id=submission_id)
        submission.approved = True
        submission.save()

    return render(request, 'submissions/approve_submissions.html', {'submissions': submissions})



from .decorators import supervisor_required
from feedback.models import Feedback
@login_required
@supervisor_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    supervisor = SupervisorProfile.objects.get(user=request.user)

    # mark as seen
    if not submission.is_seen:
        submission.is_seen = True
        submission.save()

    # ✅ get all submissions by this student (latest first)
    student_submissions = Submission.objects.filter(
        student=submission.student
    ).order_by('-submitted_at')

    if request.method == "POST":
        comment = request.POST.get("feedback")

        Feedback.objects.create(
            submission=submission,
            project=submission.project,
            supervisor=supervisor,
            comment=comment
        )

        messages.success(request, "Feedback submitted successfully!")
        return redirect("submission:submission_detail", pk=submission.pk)

    return render(request, "submissions/submission_detail.html", {
        "submission": submission,
        "student_submissions": student_submissions  # ✅ pass to template
    })