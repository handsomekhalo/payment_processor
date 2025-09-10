from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from system_management.models import User, Province
# Create your models here.

class Stablecoin(models.Model):
    """
    Supported stablecoins and their blockchains (e.g., USDT on Tron).
    """
    name = models.CharField(max_length=50, unique=True)  # e.g., USDT, USDC
    symbol = models.CharField(max_length=10, unique=True)  # e.g., USDT
    blockchain = models.CharField(max_length=50)  # e.g., Ethereum, Tron, Solana
    contract_address = models.CharField(max_length=100, blank=True, null=True)  # ERC-20/TRC-20 contract address, null for native coins

    def __str__(self):
        return f"{self.symbol} ({self.blockchain})"


class MerchantWallet(models.Model):
    """
    Stores merchant wallet addresses for each stablecoin.
    """
    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallets")
    stablecoin = models.ForeignKey(Stablecoin, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)  # Allow flexibility
    is_active = models.BooleanField(default=True)  # For toggling address usage
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('merchant', 'stablecoin', 'address')

    def __str__(self):
        return f"{self.merchant.email} - {self.stablecoin.symbol} ({self.address[:8]}...)"

class Customer(models.Model):
    """
    Customer-specific data linked to merchants via transactions.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    phone_number = models.CharField(max_length=20, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.user.email}"

class Transaction(models.Model):
    """
    Records stablecoin transactions for merchants.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled'),
    )

    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    stablecoin = models.ForeignKey(Stablecoin, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=6)  # Supports stablecoin precision
    transaction_hash = models.CharField(max_length=128, unique=True, blank=True, null=True)  # Blockchain tx hash
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_request = models.ForeignKey('PaymentRequest', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.merchant.email} - {self.stablecoin.symbol} {self.amount} ({self.status})"

class PaymentRequest(models.Model):
    """
    Manages payment requests (QR codes, invoices) for merchants.
    """
    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_requests")
    stablecoin = models.ForeignKey(Stablecoin, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=6)
    wallet = models.ForeignKey(MerchantWallet, on_delete=models.CASCADE)
    request_id = models.CharField(max_length=50, unique=True)  # Unique ID for QR code/invoice
    status = models.CharField(max_length=20, choices=(
        ('OPEN', 'Open'),
        ('PAID', 'Paid'),
        ('EXPIRED', 'Expired'),
    ), default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Payment Request {self.request_id} - {self.merchant.email}"

class Report(models.Model):
    """
    Stores generated reports (e.g., daily/weekly/monthly transaction summaries).
    """
    REPORT_TYPE_CHOICES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('TAX', 'Tax/VAT'),
    )

    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    file_url = models.CharField(max_length=255)  # S3 URL or local path for CSV/PDF
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.merchant.email} - {self.report_type} Report ({self.start_date})"


class MerchantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="merchant_profile")
    business_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    compliance_status = models.CharField(
        max_length=20,
        choices=(("PENDING", "Pending"), ("VERIFIED", "Verified"), ("REJECTED", "Rejected")),
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

# class MerchantProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     business_name = models.CharField(max_length=255)
#     registration_number = models.CharField(max_length=100)
#     vat_number = models.CharField(max_length=100, blank=True, null=True)

#     # already exists
#     compliance_status = models.CharField(
#         max_length=50,
#         choices=[("PENDING", "Pending"), ("VERIFIED", "Verified"), ("REJECTED", "Rejected")],
#         default="PENDING"
#     )

#     # NEW status field
#     account_status = models.CharField(
#         max_length=20,
#         choices=[("ACTIVE", "Active"), ("SUSPENDED", "Suspended"), ("DEACTIVATED", "Deactivated")],
#         default="ACTIVE"
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.business_name

class TransactionLog(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=20)  # e.g., Detected, Confirmed, Failed
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
