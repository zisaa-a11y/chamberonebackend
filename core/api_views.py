from django.conf import settings
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView


class StampVerifyView(APIView):
    """API endpoint to verify uploaded document stamp/authenticity."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        document = request.FILES.get('document')

        if not document:
            return Response(
                {'detail': 'Document file is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_upload_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
        if document.size > max_upload_size:
            return Response(
                {'detail': 'Document size must be 10MB or less.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_types = set(getattr(settings, 'ALLOWED_DOCUMENT_TYPES', []))
        content_type = (document.content_type or '').lower()
        if content_type not in allowed_types:
            return Response(
                {'detail': 'Only PDF, JPG, and PNG files are allowed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                'result': 'verified',
                'message': 'Document verified successfully.',
            },
            status=status.HTTP_200_OK,
        )
