

from crypto_payment_management.models import MerchantProfile
# from system_management.api import serializers
from crypto_payment_management.api import serializers
from rest_framework import serializers
from system_management.models import Profile  # correct model



class CreateMerchantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantProfile
        fields = ["id", "user", "business_name", "registration_number", "vat_number", "compliance_status", "created_at"]
        read_only_fields = ["id", "compliance_status", "created_at"]

    def validate(self, data):
        user = data.get("user")
        if not user:
            raise serializers.ValidationError({"user": "User is required"})
        if not hasattr(user, "user_type") or user.user_type.name.upper() != "MERCHANT":
            raise serializers.ValidationError({"user": "User must be of type MERCHANT"})
        return data



# For retrieving Merchant Profile details

class GetMerchantProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # returns user's email or __str__

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "province",
            # "city",
            # "street_address",
            # "postal_code",
            # "phone_number",
            "business_name",
            "business_registration_number",
            "vat_number",
        ]

