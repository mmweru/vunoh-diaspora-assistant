# Helper for CSRF exemption on API endpoints
from functools import wraps
from django.views.decorators.csrf import csrf_exempt

def disable_csrf(view_func):
    """Decorator to disable CSRF for a view"""
    return csrf_exempt(view_func)
