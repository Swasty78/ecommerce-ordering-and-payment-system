from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer, LoginSerializer
from core.utils import create_response

class RegisterView(generics.CreateAPIView):
    """
    API endpoint to register a new user.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return create_response(
            data=serializer.data,
            message="User registered successfully",
            status=status.HTTP_201_CREATED
        )

class LoginView(views.APIView):
    """
    API endpoint to authenticate a user and return JWT tokens.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = serializer.get_tokens(user)
        return create_response(
            data=tokens,
            message="Login successful",
            status=status.HTTP_200_OK
        )
