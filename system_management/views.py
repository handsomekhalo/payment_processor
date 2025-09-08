from django.conf import settings # Ensure this import is at the top

import json
import secrets
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.middleware.csrf import get_token
import requests
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from system_management import constants
from system_management.decorators import session_timeout
from system_management.general_func_classes import _send_email_thread, api_connection, host_url
from system_management.models import User, UserType
from django.http import JsonResponse
import json # You're using json.dumps, so ensure this is imported
from django.shortcuts import redirect
from django.contrib.sessions.models import Session
import json
import requests
from rest_framework import status # Import DRF status codes for clarity
# from . import constants # Ensure constants module is correctly imported for JSON_APPLICATION
import logging

logger = logging.getLogger(__name__)
import threading
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .decorators import session_timeout, check_token_in_session
# from .models import User
from system_management.api.api_helpers import send_email_api

# from .utils import host_url, api_connection, generate_password, _send_email_thread


@ensure_csrf_cookie
def csrf(request):
    """
    Sets the CSRF cookie and returns the token
    """
    token = get_token(request)
    return JsonResponse({'csrfToken': token})


def get_data_on_success(response_data):
    status = response_data.get('status')
    if status == 'success':
        data = response_data.get('data')
    else:
        data = []
    return data


def generate_password(length=12, include_digits=True, include_special_chars=True):
    letters = string.ascii_letters
    digits = string.digits if include_digits else ''
    special_chars = string.punctuation if include_special_chars else ''

    characters = letters + digits + special_chars

    length = max(length, 8)

    password = ''.join(secrets.choice(characters) for _ in range(length))

    return password



def set_csrf_token(request):
     response = JsonResponse({'detail': 'CSRF cookie set'})
     response.set_cookie('csrftoken', get_token(request)) 
     return response



# View that redirects to Next.js
def login_view(request):
    return redirect("http://localhost:3000/")  # Next.js is running here
    # return redirect('http://52.14.111.23:3000/')  # or your real domain



@csrf_exempt
def register_user(request):
    
    if request.method != 'POST':
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed"
        }, status=405)

    try:
        # Parse request data
        data = json.loads(request.body)

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Check if all fields are provided
        if not all([first_name, last_name, email, password, confirm_password]):
            return JsonResponse({
                "status": "error",
                "message": "All fields are required."
            }, status=400)

        # Check if password matches confirm_password
        if password != confirm_password:
            return JsonResponse({
                "status": "error",
                "message": "Passwords do not match."
            }, status=400)

        # Prepare API call to register user
        url = f"{host_url(request)}{reverse_lazy('register_api')}"
        payload = json.dumps({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        })

        headers = {
            'Content-Type': 'application/json',  # Ensure this is set correctly
        }

        # Make the API call via the api_connection helper
        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)

        # Check the response from the registration API
        if response_data and response_data.get("status") == "success":
            return JsonResponse({
                "status": "success",
                "message": "User registered successfully",
                "user_id": response_data.get("user_id")
            })

        return JsonResponse({
            "status": "error",
            "message": response_data.get("message", "Registration failed"),
            "errors": response_data.get("errors", {})
        }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON data"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Server error occurred: {str(e)}"
        }, status=500)


@ensure_csrf_cookie  # This ensures the CSRF cookie is set
def login(request):
    """User login function with API."""
    if request.method != "POST":
        return JsonResponse({
            'status': 'error', 
            'message': 'Only POST requests are allowed'
        }, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        # remember_me = data.get('rememberMe', False)

        if not email or not password:
            return JsonResponse({
                'status': 'error',
                'message': 'Email and password are required'
            }, status=400)

        # Get the existing token if any
        token = request.session.get('token')
        
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Token {token}" if token else ""
        }

        payload = json.dumps({
            'email': email,
            'password': password,
            # 'remember_me': remember_me
        })

        url = f"{host_url(request)}{reverse_lazy('login_api')}"
        
        try:
            response_data = requests.post(
                url, 
                headers=headers, 
                data=payload, 
                timeout=10
            )
            
            if response_data.status_code == 200:
                response_json = response_data.json()
                
                # Store token in session if remember_me is True
                # if remember_me and 'token' in response_json:
                #     request.session['token'] = response_json['token']
                
                return JsonResponse({
                    'status': 'success', 
                    'data': response_json
                })
            
            
            return JsonResponse({
                'status': 'error',
                'message': response_data.json().get('message', 'Login failed'),
            }, status=response_data.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'status': 'error',
                'message': f'API request failed: {str(e)}'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error', 
            'message': 'Invalid JSON data'
        }, status=400)


@csrf_exempt # Consider removing this if GET request and no state-changing operations
def get_all_users(request):
    if request.method != "GET":
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET requests are allowed'
        }, status=405)

    try:
        # --- Consolidated Token Retrieval Logic ---
        token = None # Initialize token to None *before* any checks

        # 1. Try to get token from Authorization header (most common for APIs)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Token "):
            token = auth_header.split("Token ")[-1]
        elif auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[-1]

        # 2. If no token found in headers, try session
        if not token:
            token = request.session.get("token")
        # --- End of Consolidated Token Retrieval Logic ---

        if not token:
            logger.warning("Authorization token missing from headers and session for get_all_users.")
            return JsonResponse({
                "status": "error",
                "message": "Authorization token is required and not found."
            }, status=401)

        # Persist token in session (optional, but harmless if needed)
        request.session["token"] = token
        request.session.modified = True

        # --- API call to fetch users ---
        # USE INTERNAL_API_BASE_URL for internal calls
        users_api_url = f"{settings.INTERNAL_API_BASE_URL}{reverse('get_users_api')}"
        
        payload = json.dumps({
            'token': token  # Adding token to payload
        })


        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': constants.JSON_APPLICATION
        }

        # REMOVE PAYLOAD FOR GET REQUESTS
        response_data_users = api_connection(method="GET", url=users_api_url, headers=headers,data=payload)
        # response_data = api_connection(method="GET", url=url, headers=headers, data=payload)

        users = []
        if response_data_users and response_data_users.get('status') == 'success':
            users = response_data_users.get('users', [])
        else:
            # Log error if internal user API call failed
            logger.error(f"Internal API call to get_users_api failed: {response_data_users.get('message', 'No message')}")
            # Potentially return an error here if users data is critical for this endpoint
            # For now, we'll let it proceed with an empty list.

        # --- API call to fetch user types (roles) ---
        # USE INTERNAL_API_BASE_URL for internal calls
        roles_api_url = f"{settings.INTERNAL_API_BASE_URL}{reverse_lazy('get_user_types_api')}"

        # REMOVE PAYLOAD FOR GET REQUESTS
        response_data_roles = api_connection(method="GET", url=roles_api_url, headers=headers, data=payload)

        roles = []
        if response_data_roles and response_data_roles.get('status') == 'success':
            roles = response_data_roles.get('user_types', [])
        else:
            # Log error if internal roles API call failed
            logger.error(f"Internal API call to get_user_types_api failed: {response_data_roles.get('message', 'No message')}")
            # For now, we'll let it proceed with an empty list.


        return JsonResponse({
            'status': 'success',
            'users': users,
            'user_types': roles
        }, status=200) # Explicitly set status 200 for success

    except requests.exceptions.RequestException as e:
        logger.exception(f"Network or API call error in get_all_users view: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f"Could not connect to internal service: {str(e)}"
        }, status=500)
    except Exception as e:
        logger.exception("An unexpected server error occurred in get_all_users view.")
        return JsonResponse({
            'status': 'error',
            'message': f"Server error occurred: {str(e)}. Please check server logs."
        }, status=500)



# Assuming host_url and api_connection are defined elsewhere and accessible
# Example placeholders if they are not:
# def host_url(request):
#     return f"{request.scheme}://{request.get_host()}"
#
# def api_connection(method, url, headers, data=None):
#     # This function needs to handle the actual requests.get/post etc.
#     # And return a consistent dictionary. Your previous code had a direct requests.get call.
#     # Let's revert to a direct requests.get for simplicity if api_connection isn't robust.
#     # If api_connection is well-tested and robust, keep it.
#     # For now, I'll provide the fixed token logic and assume api_connection works or is replaced.
#     pass # Placeholder - you need your actual api_connection or replace with direct requests.get

@csrf_exempt # Consider removing this if GET request and no state-changing operations
def get_roles(request):
    """
    View function to get all roles/user types.
    Handles both session and header-based token authentication.
    """

    if request.method != "GET":
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET requests are allowed'
        }, status=405)

    try:
        # --- Consolidated Token Retrieval Logic ---
        token = None # Initialize token to None *before* any checks

        # 1. Try to get token from Authorization header (most common for APIs)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Token "):
            token = auth_header.split("Token ")[-1]
        elif auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[-1]

        # 2. If no token found in headers, try session
        if not token:
            token = request.session.get("token")

        # --- End of Consolidated Token Retrieval Logic ---

        if not token:
            logger.warning("Authorization token missing from headers and session for get_roles.")
            return JsonResponse({
                "status": "error",
                "message": "Authorization token is required and not found."
            }, status=401)

        # Persist token in session for later use (optional, but harmless if needed)
        request.session["token"] = token
        request.session.modified = True

        # Construct internal API URL
        # Ensure settings.INTERNAL_API_BASE_URL is defined and correct (as discussed previously)
        # Replacing host_url(request) with settings.INTERNAL_API_BASE_URL is highly recommended for production
        # For this fix, I'll keep host_url(request) as per your provided code, but be aware of its potential issues.
        # url = f"{host_url(request)}{reverse('get_user_types_api')}" # Consider settings.INTERNAL_API_BASE_URL
        url = f"{settings.INTERNAL_API_BASE_URL}{reverse('get_user_types_api')}"

        payload = json.dumps({
            'token': token
        })



        headers = {
            'Authorization': f'Token {token}', # 'token' is now guaranteed to be defined (or caught by the if not token block)
            'Content-Type': constants.JSON_APPLICATION # Ensure constants.JSON_APPLICATION is correctly imported
        }

        # Your original code used json.dumps(payload={'token':token}) with a GET request
        # GET requests typically don't have a request body (payload).
        # The 'token' should be in the Authorization header, which you're doing.
        # If your internal API *requires* the token in the body for GET requests, that's unusual.
        # I'll comment out the payload for GET, as it's generally incorrect.
        # If your api_connection requires 'data' even for GET, ensure it handles it without breaking.
        # payload = json.dumps({'token': token}) # This is likely not needed for a GET request

        # If api_connection handles requests.get directly without 'data' for GET:
        response_data = api_connection(
            method="GET",
            url=url,
            headers=headers,
            data=payload

            # data=payload # Removed for GET request, typically not used
        )

        # Your api_connection function should return a dict with 'status' and 'message'
        # or raise an exception that gets caught.
        if response_data and response_data.get('status') == 'success':
            return JsonResponse({
                'status': 'success',
                'data': { # Consistent with previous output format
                    'roles': response_data.get('user_types', [])
                },
                'message': "" if response_data.get('user_types') else "No roles found."
            }, status=200)
        else:
            # Handle cases where api_connection returns an error status or malformed response
            message = response_data.get('message', 'Failed to fetch roles from internal API.') if response_data else 'Internal API did not return a valid response.'
            status_code = response_data.get('status_code', 400) if isinstance(response_data, dict) and 'status_code' in response_data else 400
            return JsonResponse({
                'status': 'error',
                'message': message
            }, status=status_code)

    except requests.exceptions.RequestException as e:
        logger.exception(f"Network or API call error while fetching roles from internal API: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f"Could not connect to internal role service: {str(e)}"
        }, status=500)
    except Exception as e:
        logger.exception("An unexpected server error occurred in get_roles view.")
        return JsonResponse({
            'status': 'error',
            'message': f"Server error occurred: {str(e)}. Please check server logs."
        }, status=500)
    


@csrf_exempt
def create_user(request):
    """User registration function for the creation of new users by admin"""
    
    if request.method != 'POST':
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed. Use POST."
        }, status=405)

    try:
        # Extract token from session or Authorization header
        token = request.session.get("token")
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Token "):
                token = auth_header.split("Token ")[-1]
            elif auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[-1]

        if not token:
            return JsonResponse({
                "status": "error",
                "message": "Authorization token is required."
            }, status=401)

        # Parse request data (support both POST data and JSON)
        if request.content_type == 'application/json':
            data = json.loads(request.body)

            print('data',data)
            user_type_id = data.get('user_type_id')
            
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('user_email') or data.get('email')
            phone_number = data.get('phone_number')
            # id_number = data.get('id_number')
            # passport_number = data.get('passport_number')
            # street_address = data.get('street_address')
            # suburb = data.get('suburb')
            # city = data.get('city')
            # province = data.get('province')
            # postal_code = data.get('postal_code')
        else:
            # Handle form data
            user_type_id = request.POST.get('user_type')
            # print('user_type_id', user_type_id)
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('user_email') or request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            # id_number = request.POST.get('id_number')
            # passport_number = request.POST.get('passport_number')
            # street_address = request.POST.get('street_address')
            # suburb = request.POST.get('suburb')
            # city = request.POST.get('city')
            # province = request.POST.get('province')
            # postal_code = request.POST.get('postal_code')

        # Validate required fields
        required_fields = {
            'user_type': user_type_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone_number': phone_number,
            # 'street_address': street_address,
            # 'suburb': suburb,
            # 'city': city,
            # 'province': province
        }

        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            return JsonResponse({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, status=400)

        # # Validate that either ID number or passport number is provided
        # if not id_number and not passport_number:
        #     return JsonResponse({
        #         "status": "error",
        #         "message": "Either ID number or passport number is required."
        #     }, status=400)

        # Get user created by from session
        user_created_by_id = request.session.get('user_id')
        
        # Generate password
        password = generate_password()
        confirm_password = password  # Since it's auto-generated, confirmation is the same

        # Prepare API payload
        url = f"{host_url(request)}{reverse('create_users_api')}"
        payload = json.dumps({
            "user_type_id": int(user_type_id),
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
            "phone_number": phone_number,
            # "id_number": id_number or "",
            # "passport_number": passport_number or "",
            # "street_address": street_address,
            # "suburb": suburb,
            # "city": city,
            # "province": province,
            # "postal_code": postal_code or "",
            "user_created_by": user_created_by_id
        })

        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': constants.JSON_APPLICATION
        }

        # Make API call to create user
        response_data = api_connection(method="POST", url=url, headers=headers, data=payload)
        status_result = response_data.get('status')

        if status_result == 'success':
            email_templates = {
                '1': "email_temps/admin_credentials.html",
            }
            
            html_tpl_path = email_templates.get(str(user_type_id), "email_temps/user_credentials.html")
            
            subject = "New User Registration - Account Created"
            login_url = f"{host_url(request)}{reverse('login_view')}"
            receiver_email = email
            
            context_data = {
                "login_url": login_url,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone_number": phone_number,
                "password": password,
                "user_type": user_type_id,
                # "street_address": street_address,
                # "suburb": suburb,
                # "city": city,
                # "province": province,
                # "postal_code": postal_code
            }

            # Prepare email API call
            email_url = f"{host_url(request)}{reverse('send_email_api')}"
            email_payload = json.dumps({
                "html_tpl_path": html_tpl_path,
                "receiver_email": receiver_email,
                "context_data": context_data,
                "subject": subject,
            })

            # Send email in separate thread
            thread = threading.Thread(
                target=_send_email_thread, 
                args=(email_url, headers, email_payload)
            )
            thread.start()

            # Return success response
            return JsonResponse({
                "status": "success",
                "message": "User created successfully. Login credentials sent via email.",
                "user": response_data.get('user', {}),
                "user_id": response_data.get('user', {}).get('id')
            })
        else:
            # Return error from API
            return JsonResponse({
                "status": "error",
                "message": response_data.get('message', 'User creation failed')
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON data"
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            "status": "error",
            "message": f"Invalid data format: {str(e)}"
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "status": "error",
            "message": f"Server error occurred: {str(e)}"
        }, status=500)
