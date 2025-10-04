import datetime
from datetime import datetime
import json
import random
from requests import Response
from system_management import constants
# from system_management.api.serializers import DeleteUserSerializer, GetAlltUserModelSerializer, RegisterSerializer, UserModelSerializer, UserTypeModelSerializer, UserUpdateSerializer,CreateUserSerializer
from system_management.api.serializers import DeleteUserSerializer, GetAlltUserModelSerializer, CreateUserSerializer, UserModelSerializer, UserTypeModelSerializer, UserUpdateSerializer
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

    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



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

@api_view(['POST', 'PUT'])
def update_user_api(request):
    print('executing update_user_api')
    if request.method == 'POST':
        try:
            # More robust way to parse request body
            if isinstance(request.body, bytes) and request.body:
                try:
                    body = json.loads(request.body)
                except json.JSONDecodeError:
                    print("Failed to parse JSON from bytes body")
                    body = request.data
            else:
                body = request.data
            
            
            # If body is empty or None, use request.data
            if not body:
                body = request.data
            
            serializer = UserUpdateSerializer(data=body)

            if serializer.is_valid():
                validated_data = serializer.validated_data
                user_id = validated_data.get('user_id')
                email = validated_data.get('email')

                # Check for duplicate email
                if User.objects.exclude(id=user_id).filter(email=email).exists():
                    return Response({
                        'status': "error",
                        'message': f"User with email {email} already exists."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Fetch the user
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return Response({
                        'status': "error",
                        'message': f"User with id {user_id} does not exist."
                    }, status=status.HTTP_400_BAD_REQUEST)

                user_type_id = validated_data.get('user_type_id')
                try:
                    user_type = UserType.objects.get(id=user_type_id)
                except UserType.DoesNotExist:
                    return Response({
                        'status': "error",
                        'message': f"User type with id {user_type_id} does not exist."
                    }, status=status.HTTP_400_BAD_REQUEST)

                email_change = False
                if not user.email == validated_data.get('email'):
                    email_change = True

                # Update user data
                user.first_name = validated_data.get('first_name')
                user.last_name = validated_data.get('last_name')
                user.email = validated_data.get('email')
                user.user_type_id = user_type.id
                user.save()

                return Response({
                    'status': "success",
                    'message': "User updated successfully.",
                    'user_type': str(user_type.name).lower(),
                    "email_change": email_change
                }, status=status.HTTP_200_OK)

            else:
                print('Serializer errors:', serializer.errors)
                return Response({
                    'status': "error",
                    'message': str(serializer.errors)
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Exception in update_user_api: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'status': "error",
                'message': f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({
            'status': "error",
            'message': "Invalid request method. Use POST."
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["POST"])
# @permission_classes((AllowAny,))
def delete_user_api(request):
    """
    Deletes a user and their profile by email.
    Accepts email in body (JSON or form-data) or query param.
    """
    try:
        # Handle request data - DRF automatically parses JSON
        body = request.data
        print('body_________________________', body)
        print('body type:', type(body))
        
        # Handle case where body might be a string (needs parsing)
        if isinstance(body, str):
            try:
                body = json.loads(body)
                print('parsed body:', body)
            except json.JSONDecodeError:
                return Response({
                    "status": "error",
                    "message": "Invalid JSON format in request body."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        print('passed statement')

        # Get email from body or query params
        email = body.get("email") if isinstance(body, dict) else None
        if not email:
            email = request.query_params.get("email")
        print('email ***********************', email)
        
        if not email:
            print('no email')
            return Response({
                "status": "error",
                "message": "Email is required to delete a user."
            }, status=status.HTTP_400_BAD_REQUEST)

        print('going into serializer')
        
        # Validate email format (assuming you have a DeleteUserSerializer)
        serializer = DeleteUserSerializer(data={"email": email})
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists before trying to delete
        try:
            user = User.objects.get(email=email)
            user.delete()
            
            return Response({
                "status": "success",
                "message": f"User with email {email} has been deleted."
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"User with email {email} does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

    except json.JSONDecodeError:
        return Response({
            "status": "error",
            "message": "Invalid JSON format in request body."
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import traceback
        traceback.print_exc()  # This will help you see the full error in console
        return Response({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)