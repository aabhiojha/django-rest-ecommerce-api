from django.core.exceptions import ValidationError
from django.db import models
import re


def validate_website(url):
    """Function to validate URL using a regular expression"""
    url_regex = re.compile(
        r"^(https?://)?"  # Optional http or https protocol
        r"(www\.)?"  # Optional 'www.'
        r"([a-zA-Z0-9-]+\.)+"  # One or more subdomains/domain parts
        r"[a-zA-Z]{2,6}"  # Top-level domain (e.g., .com, .org)
        r"(/[\w\s./?#-]*)*$"  # Optional path, query, and fragment components
    )

    return re.match(url_regex, url) is not None


def validate_phone(phone):
    """A function to validate the phone number accoriding to nepal format"""
    url_regex = re.compile(
        r"(+977)?" # means +977 is optional 
        r"^[0-9]{10}$" # 10 digits compulsory
        )
    return re.match(url_regex, phone)