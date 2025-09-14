from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from core.models import BaseModel


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Override groups and user_permissions to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name="groups",
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_permissions_set",
        related_query_name="user",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.email


class UserProfile(BaseModel):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("othe", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_picture = models.ImageField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, blank=True)

    def __str__(self):
        return f"{self.user.email}'s profile"


class Address(BaseModel):
    user = models.ForeignKey(User, related_name="addresses", on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    address_descripton = models.CharField(max_length=200)
    is_primary = models.BooleanField(default=False)
