

from crypto_payment_management.models import MerchantProfile, MerchantWallet
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



class MerchantProfileUpdateSerializer(serializers.Serializer):
    merchant_id = serializers.IntegerField(required=True)
    business_name = serializers.CharField(max_length=255, required=False)
    business_registration_number = serializers.CharField(max_length=100, required=False)
    vat_number = serializers.CharField(max_length=100, required=False)
    # phone_number = serializers.CharField(max_length=20, required=False)
    street_address = serializers.CharField(max_length=255, required=False)
    # suburb = serializers.CharField(max_length=255, required=False)
    # city = serializers.CharField(max_length=255, required=False)
    province = serializers.IntegerField(required=False)
        # postal_code = serializers.CharField(max_length=10, required=False)


class MerchantWalletSerializer(serializers.ModelSerializer):
    stablecoin_name = serializers.CharField(source="stablecoin.name", read_only=True)
    stablecoin_symbol = serializers.CharField(source="stablecoin.symbol", read_only=True)
    blockchain = serializers.CharField(source="stablecoin.blockchain", read_only=True)

    class Meta:
        model = MerchantWallet
        fields = ["id", "merchant", "stablecoin", "stablecoin_name", "stablecoin_symbol", "blockchain", "address", "is_active", "date_added"]
        read_only_fields = ["id", "date_added", "merchant"]


class CreateMerchantWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantWallet
        fields = ["stablecoin", "address"]

    def create(self, validated_data):
        merchant = self.context["request"].user
        return MerchantWallet.objects.create(merchant=merchant, **validated_data)


class UpdateMerchantWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantWallet
        fields = ["address", "is_active"]

# class MerchantStatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MerchantProfile
#         fields = ["id", "account_status"]
#         read_only_fields = ["id"]
