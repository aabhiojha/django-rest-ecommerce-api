from django.core.exceptions import ValidationError


def validate_price(value):
    if value < 0:
        raise ValidationError(f"Negative value is not accepted")
