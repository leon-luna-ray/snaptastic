from django.shortcuts import render
from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer

# /user/login
@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(request, email=email, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(instance=user)
        return Response({"token": token.key, "user": serializer.data})
    else:
        return Response(
            {"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
        )

# /user/logout
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )
    except Token.DoesNotExist:
        return Response(
            {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
        )


# /user/signup
@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = serializer.instance
        user.set_password(request.data["password"])
        user.save()
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key, "user": serializer.data})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /users/whoami
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response(f"passed for {request.user.email}")
