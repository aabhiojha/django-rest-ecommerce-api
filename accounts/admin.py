from django.contrib import admin

from .models import User, UserProfile, Address

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Address)
