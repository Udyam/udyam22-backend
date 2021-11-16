from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import (
    ResetPasswordEmailSerializer,
    NewPasswordSerializer,
    RegisterSerializer,
    check,
    LoginSerializer,
    UserSerializer,
)
from .models import UserAccount, validate_phone_number
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    force_str,
    smart_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.urls import reverse
from .utils import Util, part1, part2, part3, part4
from rest_framework.authtoken.models import Token


class LoginView(generics.GenericAPIView):
    """
    TODO:
    Implement login functionality, taking username and password
    as input, and returning the Token.
    """

    serializer_class = LoginSerializer

    def post(self, request):
        email_or_username = request.data.get("email_or_username")
        password = request.data.get("password")
        if email_or_username is None or password is None:
            return Response(
                {"error": "Please provide both username and password"}, status=400
            )

        user = authenticate(username=email_or_username, password=password)
        if not user or user.is_active == False:
            return Response(
                {"error": "User not authorized!"}, status=status.HTTP_401_UNAUTHORIZED
            )
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class LogoutView(generics.GenericAPIView):
    """
    TODO:
    Implement logout functionality, logout the user.
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LoginSerializer

    def get(self, request):
        request.user.auth_token.delete()
        logout(request)

        return Response(status=status.HTTP_200_OK)


def create_auth_token(user):
    """
    Returns the token required for authentication for a user.
    """
    token, _ = Token.objects.get_or_create(user=user)
    return token


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailSerializer

    def post(self, request):
        email = request.data["email"]

        if UserAccount.objects.filter(email=email).exists():
            user = UserAccount.objects.get(email=email)
            if user.is_active:
                return Response(
                    {"error": "User not authorized!"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )
            absurl = "http://" + current_site + relativeLink
            email_body = (
                part1
                + user.username
                + part2
                + "Click on the button to  reset your password: "
                + part3
                + absurl
                + part4
            )
            data = {
                "email_body": email_body,
                "to_mail": user.email,
                "email_subject": "Reset Your Udyam Password",
            }
            Util.send_email(data)
            return Response(
                {"success": "Link has been sent by email to reset password"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "No user with this email id exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordTokenCheckView(generics.GenericAPIView):
    serializer_class = NewPasswordSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": "Invalid token! Try again."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            return Response(
                {
                    "success": True,
                    "message": "Credentials Valid",
                    "uidb64": uidb64,
                    "token": token,
                },
                status=status.HTTP_200_OK,
            )

        except DjangoUnicodeDecodeError:
            return Response(
                {"error": "Invalid token! Try again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class NewPasswordView(generics.GenericAPIView):
    serializer_class = NewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password reset successful"},
            status=status.HTTP_200_OK,
        )


class UserUpdateView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UserAccount.objects.all()
    serializer_class = UserSerializer

    def get(self, request):
        try:
            user = request.user
            content = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "gender": user.gender,
                "year": user.year,
                "mobile": user.mobile_no,
                "college_name": user.college_name,
            }
            return Response(content, status=status.HTTP_200_OK)
        except:
            return Response(
                {"error": "An error occurred!"}, status=status.HTTP_403_FORBIDDEN
            )

    def post(self, request):
        user = UserAccount.objects.filter(username=request.user.username)
        if user is not None:
            if "first_name" in request.data:
                user.update(first_name=request.data["first_name"])
            if "last_name" in request.data:
                user.update(last_name=request.data["last_name"])
            if "gender" in request.data:
                user.update(
                    gender=request.data["gender"],
                )
            if "year" in request.data:
                user.update(
                    year=request.data["year"],
                )
            if "college_name" in request.data:
                user.update(
                    college_name=request.data["college_name"],
                )
            if "mobile" in request.data:
                validate_phone_number(request.data["mobile"])
                user.update(mobile_no=request.data["mobile"])
            return Response(
                {"message": "Updated successfully!"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "An error occurred!"}, status=status.HTTP_403_FORBIDDEN
            )


class RegisterView(generics.GenericAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = check(request.data)
            if user is None:
                user = serializer.save()
                create_auth_token(user=user)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site = get_current_site(request=request).domain
                relativeLink = reverse(
                    "activate-account", kwargs={"uidb64": uidb64, "token": token}
                )
                absurl = "http://" + current_site + relativeLink
                email_body = (
                    part1
                    + user.username
                    + part2
                    + "Click on the button to activate your account:"
                    + part3
                    + absurl
                    + part4
                )
                data = {
                    "email_body": email_body,
                    "to_mail": user.email,
                    "email_subject": "Activate Your Udyam Password",
                }
                Util.send_email(data)
                return Response(
                    {"success": "Verification link has been sent by email!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "User with same credentials already exists!"},
                    status=status.HTTP_226_IM_USED,
                )
        else:
            # print(serializer.errors)
            return Response(
                {"error": serializer.errors}, status=status.HTTP_409_CONFLICT
            )


class ActivateAccountView(generics.GenericAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = RegisterSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": "Invalid token! Try again."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user.is_active = True
            user.save()
            if user.referral_code:
                user = self.queryset.get(user_referral_code=user.referral_code)
                if user is not None:
                    user.referral_count += 1
                    user.save()
            return Response({"message": "Account verified."}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response(
                {"error": "Invalid token! Try again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )