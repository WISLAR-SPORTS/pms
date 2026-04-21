from django.core.exceptions import PermissionDenied

def supervisor_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'supervisorprofile'):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view