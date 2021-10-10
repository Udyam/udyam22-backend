from django.http import request
from rest_framework import serializers, exceptions
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import AuthenticationFailed
from .models import UserAccount,validate_phone_number
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
import random

class LoginSerializer(serializers.ModelSerializer):
    email_or_username = serializers.CharField()
    class Meta:
        model = UserAccount
        fields = ('email_or_username', 'password')
        
class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']


class NewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6)
    token = serializers.CharField(min_length=1)
    uidb64 = serializers.CharField(min_length=1)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, data):
        try:
            password = data.get('password')
            token = data.get('token')
            uidb64 = data.get('uidb64')
            id = force_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=id)

            if PasswordResetTokenGenerator().check_token(user, token):
                user.set_password(password)
                user.save()
            else:
                raise AuthenticationFailed('The reset link is invalid', 401)

        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)

        return super().validate(data)


def check(data):
    return authenticate(username=data['username'], password=data['password'])

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500)

class RegisterSerializer(serializers.Serializer):
    # TODO: Implement register functionality
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=UserAccount.objects.all())]
            )
    username = serializers.CharField(
            required=True,
            validators=[UniqueValidator(queryset=UserAccount.objects.all())]
            )
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(
            required=True
            )
    last_name = serializers.CharField(
            required=True
            )
    gender = serializers.CharField(
            required=True
            )
    year = serializers.CharField(
            required=True
            )
    mobile = serializers.CharField(
            required=True,
            validators=[validate_phone_number]
            )
    college_name = serializers.CharField(
            required=True
            )
    referral_code = serializers.CharField(
            required=False,
            allow_blank=True,
            allow_null=True
            )
    class Meta:
        model = UserAccount
        fields = '__all__'
        
    def create(self, validated_data):
        user = UserAccount.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.first_name=validated_data['first_name']
        user.last_name=validated_data['last_name']
        user.gender=validated_data['gender']
        user.year=validated_data['year']
        user.college_name=validated_data['college_name']
        user.mobile_no=validated_data['mobile']
        user.referral_code=validated_data['referral_code']
        user.user_referral_code= user.first_name[0:min(len(user.first_name),5)]
        user.user_referral_code+=str(random.randint(10001,99999))
        user.save()
        return user

class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField(
            required=True
            )
    last_name = serializers.CharField(
            required=True
            )
    gender = serializers.CharField(
            required=True
            )
    year = serializers.CharField(
            required=True
            )
    mobile = serializers.CharField(
            required=True,
            validators=[validate_phone_number]
            )
    college_name = serializers.CharField(
            required=True
            )
    class Meta:
        model = UserAccount
        fields = '__all__'

    def create(self, validated_data):
        user = UserAccount.objects.get(
            username=validated_data['username'],
        )
        user.first_name=validated_data['first_name']
        user.last_name=validated_data['last_name']
        user.gender=validated_data['gender']
        user.year=validated_data['year']
        user.college_name=validated_data['college_name']
        user.mobile_no=validated_data['mobile']
        user.referral_code=validated_data['referral_code']
        user.save()
        return user