"""
Custom middleware for The Chamber One backend.
"""

import logging
from django.conf import settings


logger = logging.getLogger(__name__)


class ApiRequestLogMiddleware:
    """Log API request/response metadata for debugging production issues."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        should_log = bool(getattr(settings, 'API_REQUEST_LOGGING_ENABLED', False))

        if should_log and request.path.startswith('/api/'):
            user_id = None
            request_user = getattr(request, 'user', None)
            if request_user is not None:
                user_id = getattr(request_user, 'id', None)
            logger.info(
                'API request: method=%s path=%s user=%s',
                request.method,
                request.path,
                user_id,
            )

        response = self.get_response(request)

        if should_log and request.path.startswith('/api/'):
            logger.info(
                'API response: method=%s path=%s status=%s',
                request.method,
                request.path,
                response.status_code,
            )

        return response


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
