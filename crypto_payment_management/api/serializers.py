

from datetime import datetime, timedelta
import uuid
from crypto_payment_management.models import MerchantProfile, MerchantWallet, PaymentRequest
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





class CreatePaymentRequestSerializer(serializers.ModelSerializer):
    wallet_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PaymentRequest
        fields = ['merchant', 'stablecoin', 'amount', 'wallet_id', 'expires_at']

    def validate_wallet_id(self, value):
        try:
            wallet = MerchantWallet.objects.get(id=value, is_active=True)
        except MerchantWallet.DoesNotExist:
            raise serializers.ValidationError("Invalid wallet_id")
        return value
    
    
    
    def create(self, validated_data):
        request = self.context['request']  # grab request from serializer context
        validated_data['merchant'] = request.user  # auto-assign logged-in merchant
        wallet_id = validated_data.pop('wallet_id')
        wallet = MerchantWallet.objects.get(id=wallet_id)
        validated_data['wallet'] = wallet
        validated_data['request_id'] = str(uuid.uuid4())
        if not validated_data.get('expires_at'):
            validated_data['expires_at'] = datetime.now() + timedelta(hours=1)
        return PaymentRequest.objects.create(**validated_data)


    # def create(self, validated_data):
    #     wallet_id = validated_data.pop('wallet_id')
    #     wallet = MerchantWallet.objects.get(id=wallet_id)
    #     validated_data['wallet'] = wallet
    #     validated_data['request_id'] = str(uuid.uuid4())
    #     # Optional: auto-set expiry if not provided
    #     if not validated_data.get('expires_at'):
    #         validated_data['expires_at'] = datetime.now() + timedelta(hours=1)
    #     return PaymentRequest.objects.create(**validated_data)


class PaymentRequestSerializer(serializers.ModelSerializer):
    wallet_address = serializers.CharField(source='wallet.address', read_only=True)
    payment_uri = serializers.SerializerMethodField()

    class Meta:
        model = PaymentRequest
        fields = ['id', 'request_id', 'merchant', 'stablecoin', 'amount',
                  'wallet', 'wallet_address', 'payment_uri', 'status', 'created_at', 'expires_at']

    def get_payment_uri(self, obj):
        return f"{obj.stablecoin.blockchain.lower()}:{obj.wallet.address}?amount={obj.amount}&token={obj.stablecoin.symbol}"


class UpdatePaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRequest
        # fields = ['status']

        fields = ['status','stablecoin','amount','wallet']


# class MerchantStatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MerchantProfile
#         fields = ["id", "account_status"]
#         read_only_fields = ["id"]



