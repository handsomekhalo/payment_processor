

from requests import Response
from crypto_payment_management.api.serializers import CreateMerchantProfileSerializer, CreateMerchantWalletSerializer, CreatePaymentRequestSerializer, GetMerchantProfileSerializer, MerchantProfileUpdateSerializer, MerchantWalletSerializer, PaymentRequestSerializer, UpdateMerchantWalletSerializer, UpdatePaymentRequestSerializer
import datetime
from datetime import datetime
import json
import random
from requests import Response
from crypto_payment_management.models import MerchantProfile, MerchantWallet, PaymentRequest
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



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_merchant_profile_api(request):
    """
    Create a merchant profile for a user with type MERCHANT.
    """
    serializer = CreateMerchantProfileSerializer(data=request.data)
    if serializer.is_valid():
        merchant_profile = serializer.save()
        return Response(
            {
                "status": "success",
                "merchant_profile": CreateMerchantProfileSerializer(merchant_profile).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_merchant_profile_api(request, merchant_id):
    """
    Retrieve merchant profile details by merchant ID.
    """
    try:
        merchant_profile = MerchantProfile.objects.get(id=merchant_id)
        serializer = GetMerchantProfileSerializer(merchant_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except MerchantProfile.DoesNotExist:
        return Response(
            {"status": "error", "message": "Merchant profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )



@api_view(["POST"])
def update_merchant_profile_api(request):
    print("executing update_merchant_profile_api")
    try:
        # Parse request body
        if isinstance(request.body, bytes) and request.body:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                print("Failed to parse JSON from bytes body")
                body = request.data
        else:
            body = request.data

        if not body:
            body = request.data

        serializer = MerchantProfileUpdateSerializer(data=body)

        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response({
                "status": "error",
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        merchant_id = validated_data.get("merchant_id")

        # Fetch profile
        try:
            profile = Profile.objects.get(id=merchant_id)
        except Profile.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"Merchant profile with id {merchant_id} does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update fields dynamically
        for field, value in validated_data.items():
            if field == "province" and value:
                value = Province.objects.get(id=value)
            if field != "merchant_id":  # don’t overwrite PK
                setattr(profile, field, value)

        profile.save()

        return Response({
            "status": "success",
            "message": "Merchant profile updated successfully.",
            "merchant_id": profile.id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(["POST"])
def delete_merchant_profile_api(request):
    """
    Deletes a merchant profile by ID.
    Accepts merchant_id in JSON body or form-data.
    """
    try:
        if request.content_type == "application/json":
            body = json.loads(request.body)
        else:
            body = request.data

        merchant_id = body.get("merchant_id") or request.query_params.get("merchant_id")

        if not merchant_id:
            return Response({
                "status": "error",
                "message": "merchant_id is required to delete a merchant profile."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = Profile.objects.get(id=merchant_id)
        except Profile.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"Merchant profile with id {merchant_id} does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)

        profile.delete()

        return Response({
            "status": "success",
            "message": f"Merchant profile with id {merchant_id} has been deleted."
        }, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_wallet_api(request, merchant_id):
    """
    Add a new wallet for a merchant.
    Merchants can only add wallets for themselves.
    """
    if request.user.id != merchant_id:
        return Response(
            {"status": "error", "message": "You are not authorized to add wallets for this merchant"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = CreateMerchantWalletSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        wallet = serializer.save()
        return Response(
            {"status": "success", "wallet": MerchantWalletSerializer(wallet).data},
            status=status.HTTP_201_CREATED,
        )
    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_wallets_api(request, merchant_id):
    """
    List all wallets for a merchant.
    Merchants can only view their own wallets.
    """
    if request.user.id != merchant_id:
        return Response(
            {"status": "error", "message": "You are not authorized to view these wallets"},
            status=status.HTTP_403_FORBIDDEN,
        )

    wallets = MerchantWallet.objects.filter(merchant_id=merchant_id, is_active=True)
    serializer = MerchantWalletSerializer(wallets, many=True)
    return Response({"status": "success", "wallets": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_wallet_api(request, wallet_id):
    """
    Update wallet address or status.
    Merchants can only update their own wallets.
    """
    try:
        wallet = MerchantWallet.objects.get(id=wallet_id, is_active=True)
    except MerchantWallet.DoesNotExist:
        return Response({"status": "error", "message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

    if wallet.merchant != request.user:
        return Response(
            {"status": "error", "message": "You are not authorized to update this wallet"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = UpdateMerchantWalletSerializer(wallet, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"status": "success", "wallet": MerchantWalletSerializer(wallet).data},
            status=status.HTTP_200_OK,
        )
    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_wallet_api(request, wallet_id):
    """
    Deactivate (soft delete) a wallet.
    Merchants can only delete their own wallets.
    """
    try:
        wallet = MerchantWallet.objects.get(id=wallet_id, is_active=True)
    except MerchantWallet.DoesNotExist:
        return Response({"status": "error", "message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

    if wallet.merchant != request.user:
        return Response(
            {"status": "error", "message": "You are not authorized to delete this wallet"},
            status=status.HTTP_403_FORBIDDEN,
        )

    wallet.is_active = False
    wallet.save()
    return Response(
        {"status": "success", "message": "Wallet deactivated successfully"},
        status=status.HTTP_200_OK,
    )

# @api_view(["PATCH"])
# def suspend_merchant(request, pk):
#     try:
#         merchant = MerchantProfile.objects.get(pk=pk)
#     except MerchantProfile.DoesNotExist:
#         return Response({"error": "Merchant not found"}, status=status.HTTP_404_NOT_FOUND)

#     serializer = MerchantStatusSerializer(merchant, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payment_request_api(request):
    """
    Merchant/uperadmin creates a payment request (invoice / QR code)
    """
    # enforce merchant ownership
    # if request.user.user_type != "MERCHANT": or request.user.user_type != "ADMIN":
    #     return Response({"status": "error", "message": "Only merchants can create payment requests"},
    #                     status=status.HTTP_403_FORBIDDEN)
    # enforce merchant or admin ownership
    # if request.user.user_type != "MERCHANT" and request.user.user_type != "ADMIN":
    if request.user.user_type.name != "MERCHANT" and request.user.user_type.name != "ADMIN":

        return Response({"status": "error", "message": "Only merchants and admins can create payment requests"},
                        status=status.HTTP_403_FORBIDDEN)

    # serializer = CreatePaymentRequestSerializer(data=request.data)
    serializer = CreatePaymentRequestSerializer(data=request.data, context={"request": request})

    
    if serializer.is_valid():
        print('serializer valid')
        payment_request = serializer.save()
        return Response({"status": "success", "payment_request": PaymentRequestSerializer(payment_request).data},
                        status=status.HTTP_201_CREATED)
    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_payment_request_api(request, pk):
    """
    Retrieve one payment request
    """
    try:
        pr = PaymentRequest.objects.get(id=pk)
        if pr.merchant != request.user:
            return Response({"status": "error", "message": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = PaymentRequestSerializer(pr)
        return Response({"status": "success", "payment_request": serializer.data}, status=status.HTTP_200_OK)
    except PaymentRequest.DoesNotExist:
        return Response({"status": "error", "message": "Payment request not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_payment_requests_api(request,merchant_id ):
    
    """
    List all requests for a merchant
    """
    if str(request.user.id) != str(merchant_id):
        return Response({"status": "error", "message": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
    prs = PaymentRequest.objects.filter(merchant_id=merchant_id)
    serializer = PaymentRequestSerializer(prs, many=True)
    return Response({"status": "success", "payment_requests": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_payment_request_api(request, pk):
    """
    Update payment request status (e.g., mark expired)
    """
    try:
        pr = PaymentRequest.objects.get(id=pk)
        if pr.merchant != request.user:
            return Response({"status": "error", "message": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = UpdatePaymentRequestSerializer(pr, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "payment_request": PaymentRequestSerializer(pr).data},
                            status=status.HTTP_200_OK)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except PaymentRequest.DoesNotExist:
        return Response({"status": "error", "message": "Payment request not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_payment_request_api(request, pk):
    """
    Cancel payment request
    """
    try:
        pr = PaymentRequest.objects.get(id=pk)
        if pr.merchant != request.user:
            return Response({"status": "error", "message": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        pr.status = "CANCELLED"
        pr.save()
        return Response({"status": "success", "message": "Payment request cancelled"}, status=status.HTTP_200_OK)
    except PaymentRequest.DoesNotExist:
        return Response({"status": "error", "message": "Payment request not found"}, status=status.HTTP_404_NOT_FOUND)