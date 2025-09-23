
from pytz import timezone
from requests import Response
from crypto_payment_management.api.serializers import CreateMerchantProfileSerializer, CreateMerchantWalletSerializer, CreatePaymentRequestSerializer, CreateTransactionSerializer, GetMerchantProfileSerializer, GetTransactionSerializer, MerchantProfileUpdateSerializer, MerchantWalletSerializer, PaymentRequestSerializer, TransactionSerializer, UpdateMerchantWalletSerializer, UpdatePaymentRequestSerializer, UpdateTransactionSerializer
import datetime
from datetime import datetime
import json
import random
from requests import Response
from crypto_payment_management.models import Customer, MerchantProfile, MerchantWallet, PaymentRequest, Stablecoin, Transaction
from customer_management.api.serializers import CustomerProfileSerializer,KYCDocumentUploadSerializer, PaymentRequestDetailSerializer, ProvinceSerializer, StablecoinSerializer, UpdateCustomerProfileSerializer
from system_management import constants
# from system_management.api.serializers import DeleteUserSerializer, GetAlltUserModelSerializer, RegisterSerializer, UserModelSerializer, UserTypeModelSerializer, UserUpdateSerializer,CreateUserSerializer
from system_management.api.serializers import DeleteUserSerializer, GetAlltUserModelSerializer, CreateUserSerializer, UserModelSerializer, UserTypeModelSerializer, UserUpdateSerializer
from system_management.models import Profile, Province, User, UserType
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
# from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes

from rest_framework import (
    status,
    permissions,
    authentication
)

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)


# ========================================
# CUSTOMER ONBOARDING & REGISTRATION
# ========================================


@api_view(["GET"])
@permission_classes([AllowAny])
def get_provinces_api(request):
    """
    Get list of available provinces for registration.
    """
    # provinces = Province.objects.all().order_by('name')
    provinces = Province.objects.all()

    serializer = ProvinceSerializer(provinces, many=True)
    return Response(
        {"status": "success", "provinces": serializer.data},
        status=status.HTTP_200_OK
    )


# ========================================
# CUSTOMER PROFILE MANAGEMENT
# ========================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_customer_profile_api(request):
    """
    Get customer profile details.
    - If the logged-in user is a customer, they can only view their own profile.
    - If the logged-in user is admin/staff, they can query any customer profile by ID/user_id.
    """
    try:
        # Parse JSON body if present
        body = {}
        if request.body:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                return Response(
                    {"status": "error", "message": "Invalid JSON format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        customer_id = body.get("id")
        user_id = body.get("user_id")

        # Case 1: Admin/Staff wants to view any profile
        if (customer_id or user_id) and request.user.is_staff:
            if customer_id:
                customer = Customer.objects.get(id=customer_id)
            else:
                customer = Customer.objects.get(user_id=user_id)

        # Case 2: Logged-in user is a customer (only fetch their own profile)
        elif request.user.user_type.name.upper() == constants.CUSTOMER:
            try:
                customer = request.user.customer_profile
            except Customer.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Customer profile not found for this user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Case 3: Non-staff, non-customer tries to query => forbidden
        else:
            return Response(
                {"status": "error", "message": "Not authorized to view this profile"},
                status=status.HTTP_403_FORBIDDEN,
            )

    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Serialize and return
    serializer = CustomerProfileSerializer(customer)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST", "PUT"])
@permission_classes([IsAuthenticated])
def update_customer_profile_api(request):
    """
    Update customer profile information.
    """
    try:
        customer = request.user.customer_profile
    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = UpdateCustomerProfileSerializer(customer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "status": "success",
                "message": "Profile updated successfully",
                "profile": CustomerProfileSerializer(customer).data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_kyc_document_api(request):
    """
    Upload KYC or FICA documents for verification.
    """
    try:
        customer = request.user.customer_profile
        serializer = KYCDocumentUploadSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Document uploaded successfully. Pending admin verification.",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_kyc_status_api(request):
    """
    Get customer's KYC verification status.
    """
    try:
        customer = request.user.customer_profile  # ensure the user is a customer
        profile = request.user.profile  # compliance info is still in Profile
    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Profile.DoesNotExist:
        return Response(
            {"status": "error", "message": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {
            "status": "success",
            "kyc_status": {
                "kyc_verified": profile.kyc_verified,
                "kyc_verified_at": profile.kyc_verified_at,
                "aml_flagged": profile.aml_flagged,
                "kyc_document_uploaded": bool(profile.kyc_document),
                "fica_document_uploaded": bool(profile.fica_document),
            }
        },
        status=status.HTTP_200_OK
    )


# ========================================
# PAYMENT PROCESSING
# ========================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_available_stablecoins_api(request):
    """
    Get list of supported stablecoins for payments.
    """
    stablecoins = Stablecoin.objects.all().order_by('symbol')
    serializer = StablecoinSerializer(stablecoins, many=True)
    return Response(
        {"status": "success", "stablecoins": serializer.data},
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_payment_request_api(request, request_id):


    cust_data = request.data
    
    print('cust_data',cust_data)
    """
    Get payment request details by QR code or request ID.
    """
    try:
        # Ensure the caller is a customer
        customer = request.user.customer_profile  
        profile = request.user.profile  

        # Check if customer is KYC verified
        if not profile.kyc_verified:
            return Response(
                {"status": "error", "message": "KYC verification required to make payments"},
                status=status.HTTP_403_FORBIDDEN,
            )


        payment_request = PaymentRequest.objects.select_related(
            "merchant", "merchant__profile", "stablecoin", "wallet"
        ).filter(request_id=request_id).first()

        if not payment_request:
            return Response(
                {"status": "error", "message": f"Payment request {request_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if it's already expired in the database
        if payment_request.status == "EXPIRED":
            return Response(
                {"status": "error", "message": "Payment request has already expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if it should be expired based on time
        if payment_request.expires_at < timezone.now():
            payment_request.status = "EXPIRED"
            payment_request.save()
            return Response(
                {"status": "error", "message": "Payment request has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if it's not OPEN status
        if payment_request.status != "OPEN":
            return Response(
                {"status": "error", "message": f"Payment request is {payment_request.status} and cannot be processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = PaymentRequestDetailSerializer(payment_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except PaymentRequest.DoesNotExist:
        return Response(
            {"status": "error", "message": "Payment request not found or already processed"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_transaction_api(request):
    """
    Create a transaction after customer makes payment.
    """
    try:
        # Ensure the caller is a customer
        customer = request.user.customer_profile
        profile = request.user.profile  

        # Check KYC
        if not profile.kyc_verified:
            return Response(
                {"status": "error", "message": "KYC verification required to make payments"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check AML
        if profile.aml_flagged:
            return Response(
                {"status": "error", "message": "Account flagged for review. Contact support."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CreateTransactionSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            transaction = serializer.save()

            # Update payment request status
            payment_request = transaction.payment_request
            payment_request.status = "PAID"
            payment_request.save()

            return Response(
                {
                    "status": "success",
                    "message": "Transaction created successfully",
                    "transaction": TransactionSerializer(transaction).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


# ========================================
# CUSTOMER WALLET & TRANSACTION HISTORY
# ========================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_customer_wallet_api(request):
    """
    Get customer wallet overview with transaction statistics.
    """
    try:
        customer = request.user.customer_profile
        
        # Get transaction statistics
        transactions = Transaction.objects.filter(customer=customer)
        
        stats = {
            'total_transactions': transactions.count(),
            'successful_transactions': transactions.filter(status='CONFIRMED').count(),
            'pending_transactions': transactions.filter(status='PENDING').count(),
            'failed_transactions': transactions.filter(status='FAILED').count(),
            'total_spent': transactions.filter(status='CONFIRMED').aggregate(
                total=Sum('amount')
            )['total'] or 0,
        }
        
        # Get recent transactions (last 10)
        recent_transactions = transactions.select_related(
            'merchant', 'merchant__profile', 'stablecoin'
        ).order_by('-created_at')[:10]
        
        wallet_data = {
            **stats,
            'recent_transactions': TransactionSerializer(recent_transactions, many=True).data
        }
        
        serializer = CustomerWalletSerializer(wallet_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_transaction_history_api(request):
    """
    Get customer's transaction history with filters.
    """
    try:
        customer = request.user.customer_profile
        
        # Get query parameters for filtering
        status_filter = request.GET.get('status')
        stablecoin_filter = request.GET.get('stablecoin')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        limit = int(request.GET.get('limit', 50))  # Default 50 transactions
        offset = int(request.GET.get('offset', 0))
        
        # Build queryset
        transactions = Transaction.objects.filter(customer=customer).select_related(
            'merchant', 'merchant__profile', 'stablecoin'
        )
        
        # Apply filters
        if status_filter:
            transactions = transactions.filter(status=status_filter.upper())
        
        if stablecoin_filter:
            transactions = transactions.filter(stablecoin__symbol=stablecoin_filter.upper())
        
        if start_date:
            try:
                start_date_parsed = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                transactions = transactions.filter(created_at__date__gte=start_date_parsed)
            except ValueError:
                return Response(
                    {"status": "error", "message": "Invalid start_date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        if end_date:
            try:
                end_date_parsed = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                transactions = transactions.filter(created_at__date__lte=end_date_parsed)
            except ValueError:
                return Response(
                    {"status": "error", "message": "Invalid end_date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # Order by most recent first
        transactions = transactions.order_by('-created_at')
        
        # Get total count for pagination
        total_count = transactions.count()
        
        # Apply pagination
        transactions = transactions[offset:offset + limit]
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(
            {
                "status": "success",
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "transactions": serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_transaction_detail_api(request, transaction_id):
    """
    Get detailed information about a specific transaction.
    """
    try:
        customer = request.user.customer_profile
        transaction = Transaction.objects.select_related(
            'merchant', 'merchant__profile', 'stablecoin', 'payment_request'
        ).get(id=transaction_id, customer=customer)
        
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Transaction.DoesNotExist:
        return Response(
            {"status": "error", "message": "Transaction not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


# ========================================
# CUSTOMER SUPPORT & UTILITIES
# ========================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_customer_merchants_api(request):
    """
    Get list of merchants customer has transacted with.
    """
    try:
        customer = request.user.customer_profile
        
        # Get unique merchants from transactions
        merchant_transactions = Transaction.objects.filter(
            customer=customer
        ).select_related('merchant', 'merchant__profile').values(
            'merchant__id',
            'merchant__email',
            'merchant__profile__business_name'
        ).distinct()
        
        merchants = []
        for mt in merchant_transactions:
            # Get transaction count and total spent with this merchant
            merchant_stats = Transaction.objects.filter(
                customer=customer,
                merchant_id=mt['merchant__id']
            ).aggregate(
                transaction_count=Count('id'),
                total_spent=Sum('amount', filter=Q(status='CONFIRMED')) or 0
            )
            
            merchants.append({
                'merchant_id': mt['merchant__id'],
                'merchant_email': mt['merchant__email'],
                'business_name': mt['merchant__profile__business_name'],
                'transaction_count': merchant_stats['transaction_count'],
                'total_spent': merchant_stats['total_spent']
            })
        
        return Response(
            {
                "status": "success",
                "merchants": merchants
            },
            status=status.HTTP_200_OK
        )
        
    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def customer_dashboard_api(request):
    """
    Get customer dashboard overview data.
    """
    try:
        customer = request.user.customer_profile
        profile = request.user.profile
        
        # Get basic stats
        total_transactions = Transaction.objects.filter(customer=customer).count()
        recent_transactions = Transaction.objects.filter(
            customer=customer
        ).select_related('merchant', 'merchant__profile', 'stablecoin').order_by('-created_at')[:5]
        
        # Get KYC status
        kyc_status = {
            'verified': profile.kyc_verified,
            'verified_at': profile.kyc_verified_at,
            'documents_uploaded': bool(profile.kyc_document and profile.fica_document),
            'flagged': profile.aml_flagged
        }
        
        # Get spending by stablecoin
        spending_by_coin = Transaction.objects.filter(
            customer=customer, status='CONFIRMED'
        ).values('stablecoin__symbol').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        dashboard_data = {
            'customer_info': CustomerProfileSerializer(customer).data,
            'kyc_status': kyc_status,
            'stats': {
                'total_transactions': total_transactions,
                'spending_by_stablecoin': list(spending_by_coin)
            },
            'recent_transactions': TransactionSerializer(recent_transactions, many=True).data
        }
        
        return Response(
            {"status": "success", "dashboard": dashboard_data},
            status=status.HTTP_200_OK
        )
        
    except Customer.DoesNotExist:
        return Response(
            {"status": "error", "message": "Customer profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )