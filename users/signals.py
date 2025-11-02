from django.db.models.signals import post_save
from .models import User, UserProfile
from django.dispatch import receiver

# # to create userprofile automatically as user is created
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

