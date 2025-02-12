from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.notes.models import Note
from api.notes.serializers import NoteSerializer
from api.users.permissions import IsOwnerOrReadOnly
from api.users.models import Category

class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing notes.
    
    list:
    Return a paginated list of notes that belong to the authenticated user.
    Optionally filter by category_id using query parameter.
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Filter queryset to return only notes that belong to the authenticated user,
        optionally filtered by category_id, ordered by last updated.
        """
        queryset = Note.objects.filter(user=self.request.user)
        
        category_id = self.request.query_params.get('category_id', None)
        if category_id is not None:
            # Verify category exists and belongs to user
            category = get_object_or_404(Category, id=category_id)
            queryset = queryset.filter(category=category)
        
        return queryset.order_by('-updated_at')

    def get_object(self):
        obj = get_object_or_404(Note, id=self.kwargs['pk'], user=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)