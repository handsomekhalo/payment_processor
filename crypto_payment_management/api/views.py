

from requests import Response
from crypto_payment_management.api.serializers import CreateMerchantProfileSerializer, CreateMerchantWalletSerializer, CreatePaymentRequestSerializer, CreateTransactionSerializer, GetMerchantProfileSerializer, MerchantProfileUpdateSerializer, MerchantWalletSerializer, PaymentRequestSerializer, TransactionSerializer, UpdateMerchantWalletSerializer, UpdatePaymentRequestSerializer, UpdateTransactionSerializer
import datetime
from datetime import datetime
import json
import random
from requests import Response
from crypto_payment_management.models import MerchantProfile, MerchantWallet, PaymentRequest, Transaction
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


@api_view(["OST","DELETE"])
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
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_transaction_api(request):
    """
    Create a transaction manually (useful for testing or manual reconciliation).
    """
    serializer = CreateTransactionSerializer(data=request.data)
    if serializer.is_valid():
        tx = serializer.save()
        return Response({"status": "success", "transaction": TransactionSerializer(tx).data},
                        status=status.HTTP_201_CREATED)
    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_single_transaction_by_api(request, transaction_id):
    """
    Retrieve a single transaction by ID.
    """
    try:
        tx = Transaction.objects.get(id=transaction_id, merchant=request.user)
    except Transaction.DoesNotExist:
        return Response({"status": "error", "message": "Transaction not found."},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = TransactionSerializer(tx)
    return Response({"status": "success", "transaction": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_transactions_api(request):
    """
    List all transactions for a merchant (can filter by status or date).
    """
    status_filter = request.query_params.get("status")
    qs = Transaction.objects.filter(merchant=request.user)
    if status_filter:
        qs = qs.filter(status=status_filter)

    serializer = TransactionSerializer(qs, many=True)
    return Response({"status": "success", "transactions": serializer.data}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_transaction_api(request, transaction_id):
    """
    Update transaction status (e.g., mark as confirmed or refunded).
    """
    try:
        tx = Transaction.objects.get(id=transaction_id, merchant=request.user)
    except Transaction.DoesNotExist:
        return Response({"status": "error", "message": "Transaction not found."},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateTransactionSerializer(tx, data=request.data, partial=True)
    if serializer.is_valid():
        tx = serializer.save()
        return Response({"status": "success", "transaction": TransactionSerializer(tx).data},
                        status=status.HTTP_200_OK)
    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_transaction_api(request, transaction_id):
    """
    Delete/cancel a transaction manually.
    """
    try:
        tx = Transaction.objects.get(id=transaction_id, merchant=request.user)
    except Transaction.DoesNotExist:
        return Response({"status": "error", "message": "Transaction not found."},
                        status=status.HTTP_404_NOT_FOUND)

    tx.delete()
    return Response({"status": "success", "message": "Transaction deleted."}, status=status.HTTP_204_NO_CONTENT)


# @api_view(["POST"])
# @permission_classes([AllowAny])  # ✅ Allow webhook to hit this endpoint without login
# def blockchain_webhook_api(request):
#     try:
#         data = json.loads(request.body)
#         # Log the payload for debugging
#         print("Webhook received:", data)

#         # Optionally: verify the signature if Moralis provides one
#         # (prevents random requests from spamming your endpoint)

#         # TODO: process transaction, call create_transaction_api internally

#         return Response({"status": "ok"}, status=status.HTTP_200_OK)
#     except Exception as e:
#         print("Webhook error:", str(e))
#         return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
@permission_classes([AllowAny])
def blockchain_webhook_api(request):
    """
    Webhook endpoint for Moralis Streams.
    Receives blockchain events, extracts transactions, links to payment requests, and stores them.
    """
    try:
        payload = json.loads(request.body)
        print("Webhook received:", payload)

        txs = payload.get("txs", [])
        if not txs:
            print("No transactions found in payload, ignoring.")
            return Response({"status": "ignored"}, status=status.HTTP_200_OK)

        saved_transactions = []
        errors = []

        for tx in txs:
            tx_hash = tx.get("hash")
            to_address = tx.get("toAddress")
            from_address = tx.get("fromAddress")
            amount_wei = tx.get("value")
            confirmed = tx.get("confirmed", False)
            chain_id = payload.get("chainId")

            # ✅ Convert from WEI to ETH/USDT/etc.
            try:
                amount = int(amount_wei) / (10 ** 18)
            except Exception:
                amount = 0

            # ✅ Find the wallet in your DB
            try:
                wallet = MerchantWallet.objects.get(address__iexact=to_address, is_active=True)
            except MerchantWallet.DoesNotExist:
                print(f"No wallet found for address {to_address}, ignoring tx {tx_hash}")
                continue

            # ✅ Attempt to find a matching payment request
            payment_request = PaymentRequest.objects.filter(
                wallet=wallet,
                amount=amount,
                status="PENDING"
            ).first()

            if payment_request:
                payment_request.status = "PAID"
                payment_request.save()
                print(f"💰 PaymentRequest {payment_request.id} marked as PAID for tx {tx_hash}")

            # ✅ Build transaction data
            transaction_data = {
                "merchant": wallet.merchant.id,
                "stablecoin": wallet.stablecoin.id,
                "amount": amount,
                "transaction_hash": tx_hash,
                "status": "CONFIRMED" if confirmed else "PENDING",
                "payment_request": payment_request.id if payment_request else None,
            }

            serializer = TransactionSerializer(data=transaction_data)
            if serializer.is_valid():
                saved = serializer.save()
                saved_transactions.append(saved.id)
                print(f"✅ Transaction {tx_hash} saved for merchant {wallet.merchant.id}")
            else:
                print(f"❌ Serializer error for {tx_hash}: {serializer.errors}")
                errors.append({"tx_hash": tx_hash, "errors": serializer.errors})

        return Response(
            {"status": "processed", "saved_transactions": saved_transactions, "errors": errors},
            status=status.HTTP_201_CREATED if saved_transactions else status.HTTP_200_OK,
        )

    except Exception as e:
        print("Webhook error:", str(e))
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    # @api_view(["POST"])
    # @permission_classes([AllowAny])
    # def blockchain_webhook_api(request):
    #     """
    #     Receive blockchain transaction events from Moralis and save them.
    #     """
    #     try:
    #         payload = json.loads(request.body)
    #         print("Webhook received:", payload)

    #         # ✅ 1. Extract relevant fields from Moralis payload
    #         tx_hash = payload.get("txHash") or payload.get("transaction_hash")
    #         to_address = payload.get("to")
    #         from_address = payload.get("from")
    #         amount = payload.get("value")  # usually in smallest unit (wei for ETH)
    #         token_symbol = payload.get("tokenSymbol", "USDT")
    #         chain_id = payload.get("chainId")

    #         # ✅ 2. Find the matching merchant wallet
    #         # from system_management.models import MerchantWallet, Stablecoin
    #         try:
    #             wallet = MerchantWallet.objects.get(address__iexact=to_address, is_active=True)
    #         except MerchantWallet.DoesNotExist:
    #             print(f"No wallet found for address {to_address}, ignoring transaction")
    #             return Response({"status": "ignored"}, status=status.HTTP_200_OK)

    #         # ✅ 3. Convert amount to proper decimals if needed
    #         # For MVP, assume Moralis sends human-readable amount
    #         # In production, you'd divide by 10**token_decimals

    #         transaction_data = {
    #             "merchant": wallet.merchant.id,
    #             "stablecoin": wallet.stablecoin.id,
    #             "amount": amount,
    #             "transaction_hash": tx_hash,
    #             "status": "PENDING",  # you can set CONFIRMED if Moralis confirms
    #             "payment_request": None,  # can link if you pass requestId in metadata
    #         }

    #         serializer = TransactionSerializer(data=transaction_data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({"status": "success", "transaction": serializer.data}, status=status.HTTP_201_CREATED)
    #         else:
    #             print("Serializer errors:", serializer.errors)
    #             return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    #     except Exception as e:
    #         print("Webhook error:", str(e))
    #         return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
