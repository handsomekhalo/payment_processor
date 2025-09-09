"""Urls for the api views of system_management app"""
from django.urls import path
import system_management.api.views as views
import crypto_payment_management.api.views as views
from system_management.api.api_helpers import send_email_api



urlpatterns = [

    path('create_merchant_profile_api/', views.create_merchant_profile_api, name='create_merchant_profile_api'),
    path('get_merchant_profile_api/<int:merchant_id>/', views.get_merchant_profile_api, name='get_merchant_profile_api'),

    # path('get_users_api/', views.get_users_api, name="get_users_api"),
    # path('get_user_types_api/', views.get_user_types_api, name="get_user_types_api"),
    # path('update_user_api/', views.update_user_api, name="update_user_api"),
    # path('create_users_api/', views.create_users_api, name="create_users_api"),

    # # path('logout_api/', views.logout_api, name="logout_api"),
    # # path('send_email_api/', send_email_api, name='send_email_api'),
    # path('delete_user_api/', views.delete_user_api, name='delete_user_api'),

]