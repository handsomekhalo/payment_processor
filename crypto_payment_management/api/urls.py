"""Urls for the api views of system_management app"""
from django.urls import path
import system_management.api.views as views
import crypto_payment_management.api.views as views
from system_management.api.api_helpers import send_email_api



urlpatterns = [

    path('create_merchant_profile_api/', views.create_merchant_profile_api, name='create_merchant_profile_api'),
    path('get_merchant_profile_api/<int:merchant_id>/', views.get_merchant_profile_api, name='get_merchant_profile_api'),

    path('update_merchant_profile_api/', views.update_merchant_profile_api, name="update_merchant_profile_api"),
    path('delete_merchant_profile_api/', views.delete_merchant_profile_api, name="delete_merchant_profile_api"),
    path('add_wallet_api/<int:merchant_id>/', views.add_wallet_api, name="add_wallet_api"),
    path('list_wallets_api/<int:merchant_id>/', views.list_wallets_api, name="list_wallets_api"),
    path('update_wallet_api/<int:wallet_id>/', views.update_wallet_api, name="update_wallet_api"),
    path('delete_wallet_api/<int:wallet_id>/', views.delete_wallet_api, name="delete_wallet_api"),
    path('create_payment_request_api/', views.create_payment_request_api,
        name="create_payment_request_api"),
    path('get_payment_request_api/<int:pk>/', views.get_payment_request_api, name="get_payment_request_api"),
    path('list_payment_requests_api/<int:merchant_id>/', views.list_payment_requests_api,
        name="list_payment_requests_api"),
    path('update_payment_request_api/<int:pk>/', views.update_payment_request_api, name="update_payment_request_api"),
    path('delete_payment_request_api/<int:pk>/', views.delete_payment_request_api, name="delete_payment_request_api"),

    


        




    # path('create_users_api/', views.create_users_api, name="create_users_api"),

    # # path('logout_api/', views.logout_api, name="logout_api"),
    # # path('send_email_api/', send_email_api, name='send_email_api'),
    # path('delete_user_api/', views.delete_user_api, name='delete_user_api'),

]