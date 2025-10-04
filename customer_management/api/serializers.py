from pytz import timezone
from crypto_payment_management.api import serializers
from rest_framework import serializers
from crypto_payment_management.models import Customer, PaymentRequest, Stablecoin, Transaction
from system_management import constants
from system_management.models import Profile, Province, User, UserType


class CustomerProfileSerializer(serializers.ModelSerializer):
    # User fields
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    # Customer field
    phone_number = serializers.CharField(read_only=True)

    # Profile fields
    kyc_status = serializers.BooleanField(source="user.profile.kyc_verified", read_only=True)
    kyc_verified_at = serializers.DateTimeField(source="user.profile.kyc_verified_at", read_only=True)
    aml_flagged = serializers.BooleanField(source="user.profile.aml_flagged", read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "kyc_status",
            "kyc_verified_at",
            "aml_flagged",
            "date_created",
        ]


class UpdateCustomerProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)

    # Customer fields
    phone_number = serializers.CharField(max_length=20, required=False)

    # Profile fields
    province_id = serializers.IntegerField(required=False)
    street_address = serializers.CharField(max_length=255, required=False)
    suburb = serializers.CharField(max_length=255, required=False)
    city = serializers.CharField(max_length=255, required=False)
    postal_code = serializers.CharField(max_length=10, required=False)
    passport_number = serializers.CharField(max_length=255, required=False, allow_blank=True)
    kyc_verified = serializers.BooleanField(required=False)
    aml_flagged = serializers.BooleanField(required=False)

    def validate_province_id(self, value):
        if value and not Province.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid province selected.")
        return value

    def update(self, instance, validated_data):
        """
        instance = Customer
        instance.user = User
        instance.user.profile = Profile
        """
        # --- User fields ---
        user_fields = ['first_name', 'last_name', 'email']
        for field in user_fields:
            if field in validated_data:
                setattr(instance.user, field, validated_data.pop(field))
        instance.user.save()

        # --- Customer fields ---
        if 'phone_number' in validated_data:
            instance.phone_number = validated_data.pop('phone_number')
            instance.save()

        # --- Profile fields ---
        profile = instance.user.profile
        profile_fields = [
            'street_address', 'suburb', 'city', 'postal_code',
            'passport_number', 'kyc_verified', 'aml_flagged'
        ]
        for field in profile_fields:
            if field in validated_data:
                setattr(profile, field, validated_data.pop(field))

        if 'province_id' in validated_data:
            profile.province_id = validated_data.pop('province_id')

        profile.save()

        return instance



class StablecoinSerializer(serializers.ModelSerializer):
    """
    Serializer for available stablecoins
    """
    class Meta:
        model = Stablecoin
        fields = ['id', 'name', 'symbol', 'blockchain', 'contract_address']


class PaymentRequestDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for payment request details (for customers to view)
    """
    merchant_name = serializers.CharField(source='merchant.profile.business_name', read_only=True)
    merchant_email = serializers.CharField(source='merchant.email', read_only=True)
    stablecoin_symbol = serializers.CharField(source='stablecoin.symbol', read_only=True)
    stablecoin_name = serializers.CharField(source='stablecoin.name', read_only=True)
    blockchain = serializers.CharField(source='stablecoin.blockchain', read_only=True)
    wallet_address = serializers.CharField(source='wallet.address', read_only=True)
    
    class Meta:
        model = PaymentRequest
        fields = [
            'id', 'request_id', 'merchant_name', 'merchant_email',
            'stablecoin_symbol', 'stablecoin_name', 'blockchain',
            'amount', 'wallet_address', 'status', 'created_at', 'expires_at'
        ]


class CreateTransactionSerializer(serializers.Serializer):
    """
    Serializer for creating a transaction (customer payment)
    """
    payment_request_id = serializers.CharField(max_length=50)
    transaction_hash = serializers.CharField(max_length=128)
    
    def validate_payment_request_id(self, value):
        try:
            payment_request = PaymentRequest.objects.get(request_id=value, status='OPEN')
            if payment_request.expires_at < timezone.now():
                raise serializers.ValidationError("Payment request has expired.")
            return value
        except PaymentRequest.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired payment request.")
    
    def validate_transaction_hash(self, value):
        if Transaction.objects.filter(transaction_hash=value).exists():
            raise serializers.ValidationError("Transaction hash already exists.")
        return value

    def create(self, validated_data):
        from django.utils import timezone
        
        # Get the customer from request context
        customer = self.context['request'].user.customer_profile
        
        # Get payment request
        payment_request = PaymentRequest.objects.get(
            request_id=validated_data['payment_request_id']
        )
        
        # Create transaction
        transaction = Transaction.objects.create(
            merchant=payment_request.merchant,
            customer=customer,
            stablecoin=payment_request.stablecoin,
            amount=payment_request.amount,
            transaction_hash=validated_data['transaction_hash'],
            payment_request=payment_request,
            status='PENDING'
        )
        
        return transaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for customer transaction history
    """
    merchant_name = serializers.CharField(source='merchant.profile.business_name', read_only=True)
    merchant_email = serializers.CharField(source='merchant.email', read_only=True)
    stablecoin_symbol = serializers.CharField(source='stablecoin.symbol', read_only=True)
    stablecoin_name = serializers.CharField(source='stablecoin.name', read_only=True)
    blockchain = serializers.CharField(source='stablecoin.blockchain', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'merchant_name', 'merchant_email', 'stablecoin_symbol',
            'stablecoin_name', 'blockchain', 'amount', 'transaction_hash',
            'status', 'created_at', 'updated_at'
        ]


class CustomerWalletSerializer(serializers.Serializer):
    """
    Serializer for customer wallet overview
    """
    total_transactions = serializers.IntegerField()
    successful_transactions = serializers.IntegerField()
    pending_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=18, decimal_places=6)
    recent_transactions = TransactionSerializer(many=True)


class KYCDocumentUploadSerializer(serializers.Serializer):
    """
    Serializer for KYC document uploads
    """
    document_type = serializers.ChoiceField(choices=[('kyc', 'KYC Document'), ('fica', 'FICA Document')])
    document_url = serializers.CharField(max_length=255)  # S3 URL or file path
    
    def update(self, instance, validated_data):
        profile = instance.user.profile
        document_type = validated_data['document_type']
        document_url = validated_data['document_url']
        
        if document_type == 'kyc':
            profile.kyc_document = document_url
        elif document_type == 'fica':
            profile.fica_document = document_url
            
        profile.save()
        return instance


class ProvinceSerializer(serializers.ModelSerializer):
    """
    Serializer for provinces
    """
    class Meta:
        model = Province
        fields = ['id', 'name']