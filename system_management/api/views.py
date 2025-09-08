import datetime
from datetime import datetime
import json
import random
from requests import Response
from system_management import constants
# from system_management.api.serializers import DeleteUserSerializer, GetAlltUserModelSerializer, RegisterSerializer, UserModelSerializer, UserTypeModelSerializer, UserUpdateSerializer,CreateUserSerializer
from system_management.api.serializers import GetAlltUserModelSerializer, CreateUserSerializer, UserModelSerializer, UserTypeModelSerializer
from system_management.models import Profile, User, UserType
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status


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
@permission_classes((AllowAny,))
def login_api(request):
    """
    Login api for user authentication
    Args:
        request:
    Returns:    
        Response:
        data:
            - status
            - message
        status code:
    """
    if request.method == "POST":
    
        body = json.loads(request.body)
        email = body["email"]
        password = body["password"]

        if email is None or password is None:
            data = json.dumps({
                "status": "error",
                "message": 'Please provide both username and password'
            })
            return Response(data,
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)

        if not user:

            data = json.dumps({
                "status": "error",
                "message": 'Invalid Credentials'
            })
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            data = json.dumps({
                "status": "error",
                "message": 'User is inactive, please contact admin'
            })

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        

        try:
            profile = Profile.objects.get(user_id=user.id)
            first_login = profile.first_login
            user_number = profile.phone_number

        except Profile.DoesNotExist:
            first_login = True
            user_number = ''


        otp = ''.join([str(random.randint(0, 9)) for _ in range(5)])

        # OneTimePin.objects.update_or_create(
        #     user_id=user.id,
        #     defaults={
        #         'pin': otp
        #     }
        # )

        user.last_login = datetime.now()
        user.save()

        user_serlializer = UserModelSerializer(user)

        response_data ={
            "status": "success",
            "token": token.key,
            "first_login": first_login,
            "user_number": user_number,
            "new_pin": otp,
            "user": user_serlializer.data
        }


        return Response(response_data,status=status.HTTP_200_OK)

    else:
        data = {
            'status': "error",
            'message': constants.INVALID_REQUEST_METHOD
        }
        return Response(data, status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user_api(request):
    """
    Register a new user (Customer / Merchant / Admin)
    """
    serializer = CreateUserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "status": "success",
                "user_id": user.id,
                "email": user.email,
                "user_type": user.user_type.name,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {
            "status": "error",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@permission_classes([AllowAny])
@api_view(['GET'])
def get_user_types_api(request):
    """
    Get all user types in the database

    Args:
        request:
    Returns:
        Response:
            data:
                status:
                message:
                data:
            status code:
    """
 
    if request.method == 'GET':

        user_types = UserType.objects.all()
        serializer = UserTypeModelSerializer(user_types, many=True)

        try:
            data = {
                'status': "success",
                'user_types': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)

        except KeyError:
            data = {
                'status': "error",
                'message': "Error during getting user types."
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        data = {
            'status': "error",
            'message': constants.INVALID_REQUEST_METHOD
        }
        return Response(data, status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['GET'])
def get_users_api(request):

    """
    Get all users api

    Args:
        request:
    Returns:
        Response:
            data:
                - status
                - message
                - data
            status code:
    """
    if request.method == "GET":
        users = User.objects.all()

        serializer = GetAlltUserModelSerializer(users, many=True).data

        try:
            data = {
                'status': "success",
                'users': serializer
            }
            return Response(data, status=status.HTTP_200_OK)

        except KeyError:
            data = {
                'status': "error",
                'message': "Error during getting users."
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        data = {
            'status': "error",
            'message': "Invalid request method."
        }
        return Response(data, status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(["POST"])
@permission_classes((AllowAny,))
def create_users_api(request):
    """
    Create user API for user registration
    Args:
        request: HTTP request containing user data
    Returns:
        Response:
            data:
                - status
                - message
                - user (optional)
                - token (optional)
            status code:
    """
    if request.method == "POST":
        try:
            # Parse request body
            if request.content_type == 'application/json':
                body = json.loads(request.body)
            else:
                body = request.data

            # Validate required fields
            required_fields = [
                'email', 'password', 'confirm_password', 'first_name', 
                'last_name', 'user_type_id', 
            ]
            
            missing_fields = [field for field in required_fields if not body.get(field)]
            if missing_fields:
                data = {
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            # Create serializer instance
            serializer = CreateUserSerializer(data=body)
            
            if serializer.is_valid():
                # Create user
                user = serializer.save()
                
                # Set user_created_by if provided in request
                if body.get('user_created_by'):
                    try:
                        created_by_user = User.objects.get(id=body['user_created_by'])
                        user.user_created_by = created_by_user
                        user.save()
                    except User.DoesNotExist:
                        pass  # Continue without setting created_by if user doesn't exist
                
                # Generate token for the new user
                token, _ = Token.objects.get_or_create(user=user)
                
                # Generate OTP (if needed)
                otp = ''.join([str(random.randint(0, 9)) for _ in range(5)])
                
                # Get profile information
                try:
                    profile = Profile.objects.get(user_id=user.id)
                    first_login = profile.first_login
                    user_number = profile.phone_number
                except Profile.DoesNotExist:
                    first_login = True
                    user_number = body.get('phone_number', '')
                
                # Update last login
                user.last_login = datetime.now()
                user.save()
                
                # Serialize user data
                user_serializer = UserModelSerializer(user)
                
                response_data = {
                    "status": "success",
                    "message": "User created successfully",
                    "token": token.key,
                    "first_login": first_login,
                    "user_number": user_number,
                    "new_pin": otp,
                    "user": user_serializer.data
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            else:
                # Return validation errors
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                data = {
                    "status": "error",
                    "message": "; ".join(error_messages)
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
                
        except json.JSONDecodeError:
            data = {
                "status": "error",
                "message": "Invalid JSON format"
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            data = {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        data = {
            'status': "error",
            'message': constants.INVALID_REQUEST_METHOD
        }
        return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)
