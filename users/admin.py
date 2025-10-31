from django.contrib import admin

# Register your models here.
from .models import (
    User,
    UserProfile,
    Address,
    PermissionCategory,
    Permission,
    Role,
)

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(PermissionCategory) 
admin.site.register(Permission)
admin.site.register(Role)
