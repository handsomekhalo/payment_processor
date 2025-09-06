
from system_management import constants
from system_management.models import Profile, User
from system_management.general_func_classes import BaseFormSerializer

from rest_framework import serializers
from django.contrib.auth import get_user_model
from system_management.models import UserType
from django.contrib.auth.password_validation import validate_password



class SendEmailSerializer(BaseFormSerializer):
    """Serializer for sending email"""
    context_data = serializers.DictField(
        allow_empty=True,
        required=False,
        read_only=False,
        write_only=False,
        error_messages={
            'required': 'The context data field is required.'
        }
    )
    html_tpl_path = serializers.CharField(
        max_length=100,
        required=True,
        read_only=False,
        write_only=False,
        error_messages={
            'required': 'The html_tpl_path field is required.',
            'max_length': 'The html_tpl_path field must be less than 100 characters.'
        }
    )
    subject = serializers.CharField(
        max_length=100,
        required=True,
        read_only=False,
        write_only=False,
        error_messages={
            'required': 'The subject field is required.',
            'max_length': 'The subject field must be less than 100 characters.'
        }
    )





class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id_number',
            'passport_number',
            'phone_number',
            'street_address',
            'suburb',
            'city',
            'province',
            'postal_code',
        ]

    def update(self, instance, validated_data):
        # You can add any logic here before saving
        return super().update(instance, validated_data)

    def create(self, validated_data):
        # Normally this will only be used if you're manually creating a Profile
        return Profile.objects.create(**validated_data)



class ProfileModelSerializer(serializers.ModelSerializer):
    # lockout_start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        """Metaclass for profile model serializer."""
        model = Profile
        fields = (
            'phone_number',
            'city',
            'suburb',
            'province',
            # 'first_login',
            # 'lockout_start_time',
            # 'remaining_attempts'
        )

class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer for cleaning user values"""
    user_type__name = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    profile = serializers.SerializerMethodField()

    @staticmethod
    def get_user_type__name(obj):
        """
        Get user type name
        
        :param obj:
            object type instance
        :return:
            user type name
        """
        return obj.user_type.name

    @staticmethod
    def get_profile(obj):
        """
        Get user profile
        
        :param obj:
            object type instance
        :return:
            user profile
        """
        try:
            profile = Profile.objects.get(user_id=obj.id)
            profile = ProfileModelSerializer(profile).data
        except Profile.DoesNotExist:
            profile = ''
        return profile

    class Meta:
        """Metaclass for user model serializer."""
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'last_login',
            'date_joined',
            'user_type_id',
            'user_type__name',
            'profile'
        )


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    user_type = serializers.CharField(required=False)  # e.g., CUSTOMER or MERCHANT

    # Optional profile fields
    phone_number = serializers.CharField(max_length=20, required=False)
    street_address = serializers.CharField(max_length=255, required=False)
    city = serializers.CharField(max_length=255, required=False)
    province = serializers.CharField(max_length=255, required=False)
    postal_code = serializers.CharField(max_length=10, required=False)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # Pop profile-related fields
        profile_fields = {
            "phone_number": validated_data.pop("phone_number", None),
            "street_address": validated_data.pop("street_address", None),
            "city": validated_data.pop("city", None),
            "province": validated_data.pop("province", None),
            "postal_code": validated_data.pop("postal_code", ""),
        }

        # Remove confirm_password (not needed for User)
        validated_data.pop("confirm_password")

        # Assign user type (default CUSTOMER if not passed)
        user_type_name = validated_data.pop("user_type", constants.CUSTOMER)
        try:
            user_type = UserType.objects.get(name=user_type_name.upper())
        except UserType.DoesNotExist:
            raise serializers.ValidationError({"user_type": "Invalid user type"})
        
        # Create user
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            user_type=user_type,
        )

        # Create Profile
        Profile.objects.create(
            user=user,
            **profile_fields
        )

        return user



class UserTypeModelSerializer(serializers.ModelSerializer):
    """User type model serializer for cleaning user type values"""

    class Meta:
        """Metaclass for user type model serializer."""
        model = UserType
        fields = (
            'id',
            'name'
        )



class GetAlltUserModelSerializer(serializers.ModelSerializer):
    """User model serializer for cleaning user values"""
    user_type__name = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    profile = serializers.SerializerMethodField()

    @staticmethod
    def get_user_type__name(obj):
        """
        Get user type name
        
        :param obj:
            object type instance
        :return:
            user type name
        """
        return obj.user_type.name

    @staticmethod
    def get_profile(obj):
        """
        Get user profile
        
        :param obj:
            object type instance
        :return:
            user profile
        """
        try:
            profile = Profile.objects.get(user_id=obj.id)
            profile = ProfileModelSerializer(profile).data
        except Profile.DoesNotExist:
            profile = ''
        return profile

    class Meta:
        """Metaclass for user model serializer."""
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'last_login',
            'date_joined',
            'user_type_id',
            'user_type__name',
            'profile'
        )

