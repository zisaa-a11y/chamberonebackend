"""
Custom middleware for The Chamber One backend.
"""


class DisableCSRFForAPI(object):
    """
    Disable CSRF verification for API endpoints.
    
    Since the API uses JWT authentication (not session/cookie-based),
    CSRF protection is not needed for /api/ routes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip CSRF check for all API endpoints
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)
