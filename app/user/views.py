"""
USER API VIEWS
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import *


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the API"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create Tokens for user auth"""
    serializer_class = AuthTokenSerializer  # this will override the OG serializer of ObtainAuthToken
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # uses the GUI of generics


class ManageUserView(generics.RetrieveUpdateAPIView):
    """manage the logged user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]  # chooses the mechanism of auth
    permission_classes = [permissions.IsAuthenticated]  # chooses the state of the user

    def get_object(self):
        """Retrieve and return the logged user."""
        return self.request.user  # when the user is Authenticated it gets assigned to the request of view
