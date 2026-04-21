# Auth/context_processors.py
def supervisor_links(request):
    return {
        "show_supervisor_dashboard_link": request.user.is_authenticated
                                         and getattr(request.user, "role", None) == "supervisor"
                                         and request.user.is_staff
    }