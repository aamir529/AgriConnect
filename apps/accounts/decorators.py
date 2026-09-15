from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles=[]):
    """
    Decorator that checks if the logged-in user belongs to one of the specified roles.
    Superusers bypass role restrictions for administrative oversight.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this portal.")
                return redirect('login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if request.user.role not in allowed_roles:
                messages.error(
                    request,
                    f"Access Denied. Your account role ({request.user.get_role_display()}) does not have permission to access this area."
                )
                return redirect('dashboard_router')
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
