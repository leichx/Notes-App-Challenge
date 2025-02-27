from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .permissions import IsUserOrReadOnly, IsOwnerOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, CategorySerializer

from .models import User, Category


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """
    User view set
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)

    def get_serializer_class(self):
        """
        Return the serializer class based on the action.
        """
        if self.action == "create":
            return CreateUserSerializer
        return self.serializer_class

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=False)
    def me(self, request):
        serializer = self.serializer_class(
            request.user, context={"request": request}
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class RegistrationView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializer

    def post(self, request):
        """
        Create a new user and return auth token
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'user': serializer.data,
                    'message': 'User registered successfully'
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing categories.
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        # Return both categories belonging to the authenticated user
        # and global categories that have user=None
        return Category.objects.filter(
            Q(user=self.request.user) | Q(user=None)
        )

    def perform_create(self, serializer):
        # Automatically associate the new category with the current user
        serializer.save(user=self.request.user)
