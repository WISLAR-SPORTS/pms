from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import bleach

from .forms import TestFeedbackForm


def submit_feedback(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    # 🔒 1. Rate limiting (30 seconds)
    last = request.session.get('last_feedback_time')
    if last:
        last_time = timezone.datetime.fromisoformat(last)
        if timezone.now() - last_time < timedelta(seconds=30):
            return JsonResponse({
                'success': False,
                'error': 'Please wait before submitting again'
            }, status=429)

    # 🪤 2. Honeypot spam trap
    if request.POST.get('website'):  # hidden field
        return JsonResponse({'success': False}, status=400)

    form = TestFeedbackForm(request.POST, request.FILES)

    if form.is_valid():
        feedback = form.save(commit=False)

        # 🧼 3. Sanitization (clean message)
        feedback.message = bleach.clean(
            feedback.message,
            tags=[],          # no HTML allowed
            strip=True
        )

        # 💾 Save
        feedback.save()

        # ⏱️ update rate limit
        request.session['last_feedback_time'] = timezone.now().isoformat()

        return JsonResponse({'success': True})

    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)