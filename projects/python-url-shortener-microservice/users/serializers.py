"""Serializers for user registration and authentication."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer[User]):
    """Validate and create a new user account.

    Accepts username, email, password, and password2 (confirmation).
    Enforces Django's built-in password validators.
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data: dict) -> User:
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )


class UserProfileSerializer(serializers.ModelSerializer[User]):
    """Read-only profile shape returned after register / in token payloads."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_premium", "tier"]
        read_only_fields = fields
