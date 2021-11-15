import random

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator

from .models import UserAccount


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField()

    class Meta:
        model = UserAccount
        fields = ("email", "password")


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ["email"]


class NewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6)
    token = serializers.CharField(min_length=1)
    uidb64 = serializers.CharField(min_length=1)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, data):
        try:
            password = data.get("password")
            token = data.get("token")
            uidb64 = data.get("uidb64")
            id = force_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=id)

            if PasswordResetTokenGenerator().check_token(user, token):
                user.set_password(password)
                user.save()
            else:
                raise AuthenticationFailed("The reset link is invalid", 401)

        except Exception:
            raise AuthenticationFailed("The reset link is invalid", 401)

        return super().validate(data)


def check(data):
    return authenticate(email=data["email"], password=data["password"])


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500)


class RegisterSerializer(serializers.Serializer):
    # TODO: Implement register functionality
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=UserAccount.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(required=True)
    year = serializers.CharField(required=True)
    college_name = serializers.CharField(required=True)
    referral_code = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = UserAccount
        fields = "__all__"

    def create(self, validated_data):
        user = UserAccount.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.name = validated_data["name"]
        user.year = validated_data["year"]
        user.college_name = validated_data["college_name"]
        user.referral_code = validated_data["referral_code"]
        user.user_referral_code = (user.name).replace(" ", "").lower()[: min(len(user.name), 5)]
        user.user_referral_code += str(random.randint(10001, 99999))
        user.save()
        return user


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)
    year = serializers.CharField(required=True)
    college_name = serializers.CharField(required=True)

    class Meta:
        model = UserAccount
        fields = "__all__"

    def create(self, validated_data):
        user = UserAccount.objects.get(
            email=validated_data["email"],
        )
        user.name = validated_data["name"]
        user.year = validated_data["year"]
        user.college_name = validated_data["college_name"]
        user.save()
        return user
