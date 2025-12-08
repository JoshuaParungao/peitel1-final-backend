from functools import wraps
from django.contrib.auth.views import redirect_to_login


def frontend_login_required(view_func):
    """Require both Django authentication and a frontend session flag.

    This prevents a user who logged in via `/admin/` from being
    automatically treated as logged-in for the clinic frontend unless
    they explicitly logged in through the site's login view.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        # Only allow explicit frontend-authenticated users or superusers.
        # Do NOT allow arbitrary staff accounts to bypass the frontend login.
        if not request.session.get('frontend_authenticated') and not request.user.is_superuser:
            return redirect_to_login(request.get_full_path())
        return view_func(request, *args, **kwargs)

    return _wrapped
