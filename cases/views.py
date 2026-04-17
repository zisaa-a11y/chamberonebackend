from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Case, CaseDocument, CaseTimeline, CaseNote
from .serializers import (
    CaseSerializer,
    CaseCreateSerializer,
    CaseListSerializer,
    CaseDocumentSerializer,
    CaseTimelineSerializer,
    CaseNoteSerializer,
    CaseAssignLawyerSerializer,
)
from lawyers.models import LawyerProfile


def _is_case_admin(user):
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_staff
            or getattr(user, 'role', None) == 'admin'
            or getattr(user, 'is_admin', False)
        )
    )


class IsOwnerOrLawyer(permissions.BasePermission):
    """Allow access only to case owner or assigned lawyer."""
    def has_object_permission(self, request, view, obj):
        return (
            obj.client == request.user or 
            (obj.lawyer and obj.lawyer.user == request.user) or
            _is_case_admin(request.user)
        )


class CaseAccessMixin:
    """Utility mixin for checking case-level permission on nested resources."""

    def get_case(self):
        case = get_object_or_404(
            Case.objects.select_related('lawyer', 'lawyer__user', 'client'),
            pk=self.kwargs.get('case_id')
        )
        user = self.request.user
        if not (
            case.client == user or
            (case.lawyer and case.lawyer.user == user) or
            _is_case_admin(user)
        ):
            self.permission_denied(self.request, message='Permission denied for this case.')
        return case


# Case Views
class CaseListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create cases."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'case_number', 'court_name', 'client_name']
    ordering_fields = ['created_at', 'next_hearing_date', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CaseCreateSerializer
        return CaseListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Case.objects.select_related(
            'client', 'lawyer', 'lawyer__user', 'practice_area'
        ).prefetch_related('timeline', 'documents')
        
        if _is_case_admin(user):
            return queryset
        
        if hasattr(user, 'lawyer_profile'):
            queryset = queryset.filter(lawyer=user.lawyer_profile)
        else:
            queryset = queryset.filter(client=user)
        
        # Optional filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        case = serializer.save()
        response_serializer = CaseSerializer(case, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for case detail."""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrLawyer]
    queryset = Case.objects.select_related(
        'client', 'lawyer', 'lawyer__user', 'practice_area'
    ).prefetch_related('documents', 'timeline')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CaseCreateSerializer
        return CaseSerializer


# Case Document Views
class CaseDocumentListCreateView(CaseAccessMixin, generics.ListCreateAPIView):
    """API endpoint to list and upload case documents."""
    serializer_class = CaseDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        case = self.get_case()
        return CaseDocument.objects.filter(
            case=case
        ).select_related('uploaded_by')

    def perform_create(self, serializer):
        case = self.get_case()
        serializer.save(
            case=case,
            uploaded_by=self.request.user
        )


class CaseDocumentDetailView(generics.RetrieveDestroyAPIView):
    """API endpoint for case document detail."""
    serializer_class = CaseDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = CaseDocument.objects.select_related(
            'case', 'case__client', 'case__lawyer', 'case__lawyer__user'
        )

        if _is_case_admin(user):
            return queryset

        if hasattr(user, 'lawyer_profile'):
            return queryset.filter(
                Q(case__lawyer=user.lawyer_profile) | Q(case__client=user)
            )

        return queryset.filter(case__client=user)


# Case Timeline Views
class CaseTimelineListCreateView(CaseAccessMixin, generics.ListCreateAPIView):
    """API endpoint to list and create timeline events."""
    serializer_class = CaseTimelineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        case = self.get_case()
        return CaseTimeline.objects.filter(
            case=case
        ).select_related('created_by')

    def perform_create(self, serializer):
        case = self.get_case()
        serializer.save(
            case=case,
            created_by=self.request.user
        )


class CaseTimelineDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for timeline event detail."""
    serializer_class = CaseTimelineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = CaseTimeline.objects.select_related(
            'case', 'case__client', 'case__lawyer', 'case__lawyer__user'
        )

        if _is_case_admin(user):
            return queryset

        if hasattr(user, 'lawyer_profile'):
            return queryset.filter(
                Q(case__lawyer=user.lawyer_profile) | Q(case__client=user)
            )

        return queryset.filter(case__client=user)


# Case Notes Views
class CaseNoteListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create case notes."""
    serializer_class = CaseNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        case_id = self.kwargs.get('case_id')
        user = self.request.user
        queryset = CaseNote.objects.filter(
            case_id=case_id
        ).select_related('author')
        
        # Non-lawyers can't see private notes
        if not (hasattr(user, 'lawyer_profile') or _is_case_admin(user)):
            queryset = queryset.filter(is_private=False)
        
        return queryset

    def perform_create(self, serializer):
        case_id = self.kwargs.get('case_id')
        serializer.save(
            case_id=case_id,
            author=self.request.user
        )


class CaseNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for case note detail."""
    serializer_class = CaseNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = CaseNote.objects.select_related(
            'case', 'case__client', 'case__lawyer', 'case__lawyer__user', 'author'
        )

        if _is_case_admin(user):
            return queryset

        if hasattr(user, 'lawyer_profile'):
            return queryset.filter(
                Q(case__lawyer=user.lawyer_profile) | Q(case__client=user)
            )

        return queryset.filter(case__client=user, is_private=False)


class CaseStatusUpdateView(APIView):
    """API endpoint to update case status."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            case = Case.objects.get(pk=pk)
        except Case.DoesNotExist:
            return Response(
                {'error': 'Case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user = request.user
        if not (
            case.client == user or 
            (case.lawyer and case.lawyer.user == user) or 
            _is_case_admin(user)
        ):
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in dict(Case.Status.choices):
            return Response(
                {'error': 'Invalid status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        case.status = new_status
        case.save()
        
        return Response(CaseListSerializer(case).data)


class CaseAssignLawyerView(APIView):
    """API endpoint to assign or reassign a lawyer to a case."""
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            case = Case.objects.select_related('lawyer', 'lawyer__user', 'client', 'practice_area').get(pk=pk)
        except Case.DoesNotExist:
            return Response({'error': 'Case not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CaseAssignLawyerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lawyer = self._resolve_lawyer(serializer.validated_data)
        if lawyer is None:
            return Response({'error': 'Lawyer not found.'}, status=status.HTTP_404_NOT_FOUND)

        case.lawyer = lawyer
        case.save(update_fields=['lawyer', 'updated_at'])

        response_serializer = CaseSerializer(case, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def _resolve_lawyer(self, validated_data):
        lawyer_id = validated_data.get('lawyer') or validated_data.get('assigned_lawyer')
        lawyer_name = (validated_data.get('lawyer_name') or '').strip()

        if lawyer_id:
            return LawyerProfile.objects.select_related('user').filter(pk=lawyer_id).first()

        if lawyer_name:
            parts = lawyer_name.split(' ', 1)
            if len(parts) == 2:
                return LawyerProfile.objects.select_related('user').filter(
                    Q(user__first_name__iexact=parts[0], user__last_name__iexact=parts[1]) |
                    Q(user__first_name__iexact=lawyer_name) |
                    Q(user__last_name__iexact=lawyer_name)
                ).first()

            return LawyerProfile.objects.select_related('user').filter(
                Q(user__first_name__iexact=lawyer_name) |
                Q(user__last_name__iexact=lawyer_name)
            ).first()

        return None
