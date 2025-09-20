"""Urls for the api views of system_management app"""
from django.urls import path
import customer_management.api.views as views
from system_management.api.api_helpers import send_email_api



urlpatterns = [

    path('get_provinces_api/', views.get_provinces_api, name='get_provinces_api'),
    path('get_customer_profile_api/', views.get_customer_profile_api, name='get_customer_profile_api'),
    path('update_customer_profile_api/', views.update_customer_profile_api, name="update_customer_profile_api"),
    path('get_kyc_status_api/', views.get_kyc_status_api, name='get_kyc_status_api'),
    path('upload_kyc_document_api/', views.upload_kyc_document_api, name="upload_kyc_document_api"),
    path('get_available_stablecoins_api/', views.get_available_stablecoins_api, name='get_available_stablecoins_api'),

    # path('get_merchant_profile_api/<int:merchant_id>/', views.get_merchant_profile_api, name='get_merchant_profile_api'),

    # path('update_merchant_profile_api/', views.update_merchant_profile_api, name="update_merchant_profile_api"),
    # path('delete_merchant_profile_api/', views.delete_merchant_profile_api, name="delete_merchant_profile_api"),
    # path('add_wallet_api/<int:merchant_id>/', views.add_wallet_api, name="add_wallet_api"),
    # path('list_wallets_api/<int:merchant_id>/', views.list_wallets_api, name="list_wallets_api"),
    # path('update_wallet_api/<int:wallet_id>/', views.update_wallet_api, name="update_wallet_api"),
    # path('delete_wallet_api/<int:wallet_id>/', views.delete_wallet_api, name="delete_wallet_api"),
    # path('create_payment_request_api/', views.create_payment_request_api,
    #     name="create_payment_request_api"),
    # path('get_payment_request_api/<int:pk>/', views.get_payment_request_api, name="get_payment_request_api"),
    # path('list_payment_requests_api/<int:merchant_id>/', views.list_payment_requests_api,
    #     name="list_payment_requests_api"),
    # path('update_payment_request_api/<int:pk>/', views.update_payment_request_api, name="update_payment_request_api"),
    # path('delete_payment_request_api/<int:pk>/', views.delete_payment_request_api, name="delete_payment_request_api"),
    # path("blockchain_webhook_api/",views.blockchain_webhook_api, name="blockchain_webhook"),
    # path('get_transaction_api/<int:request_id>/', views.get_transaction_api, name="get_transaction_api"),


    # path('create_users_api/', views.create_users_api, name="create_users_api"),

    # # path('logout_api/', views.logout_api, name="logout_api"),
    # # path('send_email_api/', send_email_api, name='send_email_api'),
    # path('delete_user_api/', views.delete_user_api, name='delete_user_api'),

]