import random
from datetime import timedelta
import uuid
from django.utils import timezone
from django.conf import settings
from users.models import OTP


def generate_otp(user):
    otp = str(uuid.uuid4()).split("-")[0].upper()

    # we need to make the existing active otp inactive
    # it is needed when user requests for another code in betweeen the expiry time
    OTP.objects.filter(user=user, is_active=True).update(is_active=False)

    timeout_minutes = settings.PASSWORD_RESET_TIMEOUT
    expires_at = timezone.now() + timedelta(minutes=timeout_minutes)
    
    # Create new OTP record
    OTP.objects.create(
        user=user,
        otp=otp,
        expires_at=expires_at
    )
    
    return otp
