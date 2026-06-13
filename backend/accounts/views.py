import logging

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer, UserSerializer

audit = logging.getLogger("encash.audit")


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_scope = "auth"


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_scope = "auth"


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

    def perform_create(self, serializer):
        user = serializer.save()
        audit.info("user.registered id=%s", user.id)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    """Blacklist the supplied refresh token so it can no longer be used."""

    throttle_scope = "auth"

    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response(
                {"detail": "A refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        audit.info("user.logout id=%s", request.user.id)
        return Response(status=status.HTTP_205_RESET_CONTENT)
