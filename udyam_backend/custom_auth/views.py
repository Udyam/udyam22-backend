from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import ResetPasswordEmailSerializer, NewPasswordSerializer,RegisterSerializer,check,LoginSerializer
from .models import UserAccount
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate
from django.contrib.auth import login,logout
from django.urls import reverse
from .utils import Util
from rest_framework.authtoken.models import Token

class LoginView(generics.GenericAPIView):
    """
    TODO:
    Implement login functionality, taking username and password
    as input, and returning the Token.
    """
    serializer_class = LoginSerializer

    def post(self,request):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'},
                        status=400)
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'User not authorized!'},
                        status=status.HTTP_401_UNAUTHORIZED)   
        login(request,user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class LogoutView(generics.GenericAPIView):
    """
    TODO:
    Implement logout functionality, logout the user.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LoginSerializer

    def get(self,request):
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
        serializer = self.serializer_class(data=request.data)

        email = request.data['email']

        if UserAccount.objects.filter(email=email).exists():
            user = UserAccount.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://' + current_site + relativeLink
            email_body = 'Hello '+user.username+',\nUse this link to reset your password: \n'+absurl
            data = {'email_body': email_body, 'to_mail': user.email, 'email_subject': 'Reset Your Udyam Password'}
            Util.send_email(data)
            return Response({'success': 'Link has been sent by email to reset password'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No user with this email id exists'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordTokenCheckView(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Invalid token! Try again.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Invalid token! Try again.'}, status=status.HTTP_401_UNAUTHORIZED)


class NewPasswordView(generics.GenericAPIView):
    serializer_class = NewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset successful'}, status=status.HTTP_200_OK)

class RegisterView(generics.GenericAPIView):
    queryset = UserAccount.objects.all()
    serializer_class=RegisterSerializer
    
    def post(self,request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user=check(request.data)
            if user is None:
                user=serializer.save()
                create_auth_token(user=user)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site = get_current_site(request=request).domain
                relativeLink = reverse('activate-account', kwargs={'uidb64': uidb64, 'token': token})
                absurl = 'http://' + current_site + relativeLink
                email_body = 'Hello '+user.username+',\nUse this link to activate your account: \n'+absurl
                data = {'email_body': email_body, 'to_mail': user.email, 'email_subject': 'Reset Your Udyam Password'}
                Util.send_email(data)
                return Response({'success': 'Verification link has been sent by email!'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User with same credentials already exists!'},status=status.HTTP_226_IM_USED)
        else:    
            # print(serializer.errors)
            return Response({'error': serializer.errors},status=status.HTTP_409_CONFLICT)

class ActivateAccountView(generics.GenericAPIView):
    queryset = UserAccount.objects.all()
    serializer_class=RegisterSerializer
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Invalid token! Try again.'}, status=status.HTTP_401_UNAUTHORIZED)
            user.is_active=True
            user.save()
            return Response({'message': 'Account verified.'}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Invalid token! Try again.'}, status=status.HTTP_401_UNAUTHORIZED)

