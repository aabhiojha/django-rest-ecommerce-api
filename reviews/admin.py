from django.contrib import admin

from .models import Reply, Review

admin.site.register(Review)
admin.site.register(Reply)