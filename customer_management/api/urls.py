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
    # path('get_payment_request_api/<int:request_id>/', views.get_payment_request_api, name="get_payment_request_api"),
    path('get_payment_request_api/<str:request_id>/', views.get_payment_request_api, name="get_payment_request_api"),
    path('create_transaction_api/', views.create_transaction_api, name="create_transaction_api"),
    path('get_customer_wallet_api/', views.get_customer_wallet_api, name='get_customer_wallet_api'),
    path('get_transaction_history_api/', views.get_transaction_history_api, name='get_transaction_history_api'),
    path('get_transaction_detail_api/<int:transaction_id>/', views.get_transaction_detail_api, name='get_transaction_detail_api'),
    path('get_customer_merchants_api/', views.get_customer_merchants_api, name='get_customer_merchants_api'),
    path('customer_dashboard_api/', views.customer_dashboard_api, name='customer_dashboard_api'),

]