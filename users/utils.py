import random
from datetime import timedelta
import uuid
from django.utils import timezone
from django.conf import settings
from users.models import OTP


def generate_otp(user):
    # Generate 6-digit numeric OTP
    otp = str(random.randint(100000, 999999))

    otps = OTP.objects.all()
    print(otps)

    # Calculate expiry time
    timeout_minutes = settings.PASSWORD_RESET_TIMEOUT
    expires_at = timezone.now() + timedelta(minutes=int(timeout_minutes))
    
    # Create new OTP record
    OTP.objects.create(
        user=user,
        otp=otp,
        is_active=True,
        expires_at=expires_at
    )
    
    return otp
