

from requests import Response
from crypto_payment_management.api.serializers import CreateMerchantProfileSerializer, GetMerchantProfileSerializer
import datetime
from datetime import datetime
import json
import random
from requests import Response
from crypto_payment_management.models import MerchantProfile
from system_management import constants
# from system_management.api.serializers import DeleteUserSerializer, GetAlltUserModelSerializer, RegisterSerializer, UserModelSerializer, UserTypeModelSerializer, UserUpdateSerializer,CreateUserSerializer
from system_management.api.serializers import DeleteUserSerializer, GetAlltUserModelSerializer, CreateUserSerializer, UserModelSerializer, UserTypeModelSerializer, UserUpdateSerializer
from system_management.models import Profile, User, UserType
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
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