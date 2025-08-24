from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from . import constants  # define constants.ADMIN, MERCHANT, CUSTOMER, etc.


class UserType(models.Model):
    """
    Defines different types of users:
    - Admin
    - Merchant
    - Customer
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password, first_name, last_name, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        try:
            user_type_id = UserType.objects.get(name=constants.ADMIN).id
        except ObjectDoesNotExist:
            raise ValueError(_(f'{constants.ADMIN} role not found'))
        extra_fields.update({
            'is_staff': True,
            'is_superuser': True,
            'user_type_id': user_type_id
        })
        return self.create_user(email, password, first_name="Super", last_name="Admin", **extra_fields)


class User(AbstractUser):
    """
    Core user model for merchants, customers, and admins.
    """
    username = None
    email = models.EmailField(unique=True)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    user_created_by = models.ForeignKey('self', null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='created_users')

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.user_type})"


class Profile(models.Model):
    """
    Profile stores identity, contact, and compliance details for KYC/AML.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
    # Personal details (Customers & Admins)
    id_number = models.CharField(max_length=13, null=True, blank=True)
    passport_number = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    
    # Address (for KYC/FICA)
    street_address = models.CharField(max_length=255)
    suburb = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10, default="")
    
    # Merchant-specific details
    business_name = models.CharField(max_length=255, null=True, blank=True)
    business_registration_number = models.CharField(max_length=100, null=True, blank=True)
    vat_number = models.CharField(max_length=100, null=True, blank=True)
    
    # KYC/AML compliance
    kyc_verified = models.BooleanField(default=False)
    aml_flagged = models.BooleanField(default=False)
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    first_login = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} Profile"


class Province(models.Model):
    """
    South African provinces (helps with structured address data).
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
