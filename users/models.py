from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .managers import UserManager

class User(AbstractBaseUser):
    email = models.EmailField(
        unique=True,
        db_index = True, 
        max_length=255,
        verbose_name="Email Address"
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        indexes =[
            models.Index(fields = ['email']),
            models.Index(fields = ['is_active', "is_staff"]),
        ]

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        return f"{self.first_name}" or self.email.split('@')[0]
    
    def has_permission(self, permission_code):
        if self.is_superuser:
            return True
        
        return self.user_roles.filter(
            is_active=True,
            role__is_active = True,
            role__permissions__code_name=permission_code,
            role__permissions_is_active = True
        ).exists()

    def has_all_permissions(self, permission_codes):
        if self.is_superuser:
            return True
        
        if not permission_codes:
            return True
            
        user_permissions = set(
            self.user_roles.filter(
                is_active=True,
                role__is_active=True,
                role__permissions__is_active=True
            ).values_list('role__permissions__code_name', flat=True)
        )
        
        return all(perm in user_permissions for perm in permission_codes)
    
    # def get_all_permissions(self):
    #     if self.is_superuser:
    #         return Permission.objects.filter(is_active=True)
        



class UserProfile(models.Model):
    """Extended user profile information"""
    
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="profile"
    )
    avatar = models.ImageField(
        upload_to="user_avatars/%Y/%m/", 
        blank=True, 
        null=True
    )
    bio = models.TextField(max_length=500, blank=True)
    gender = models.CharField(
        choices=GENDER_CHOICES, 
        max_length=20, 
        blank=True
    )
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.email}'s profile"




class Address(models.Model):
    """User shipping/billing addresses"""
    
    ADDRESS_TYPE_CHOICES = [
        ("home", "Home"),
        ("work", "Work"),
        ("other", "Other"),
    ]

    STATE_CHOICES = [
        ("koshi", "Koshi"),
        ("madhesh", "Madhesh"),
        ("bagmati", "Bagmati"),
        ("gandaki", "Gandaki"),
        ("lumbini", "Lumbini"),
        ("karnali", "Karnali"),
        ("sudurpashchim", "Sudurpashchim")
    ]

    user = models.ForeignKey(
        User, 
        related_name="addresses", 
        on_delete=models.CASCADE
    )
    address_type = models.CharField(
        max_length=10, 
        choices=ADDRESS_TYPE_CHOICES, 
        default="home"
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=25, choices=STATE_CHOICES)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.address_type} ({self.city})"

    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


# Rabc models

class PermissionCategory(models.Model):
    """Permissions collection for frontend purpose"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Permission Category"
        verbose_name_plural = "Permission Categories"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name
    
    def get_active_permissions(self):
        return self.permissions.filter(is_active=True)
    
    def get_permission_count(self):
        return self.permission.filter(is_active=True).count()
    
    

class Permission(models.Model):
    """Individual permission that can be assigned to roles"""
    name = models.CharField(unique=True, max_length=200)
    code_name = models.CharField(max_length=100, unique=True, db_index=True, 
                                 help_text="Unique identifier for the permission eg 'can_view_products'")
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        PermissionCategory,
        on_delete=models.CASCADE,
        related_name = "permissions"
    )