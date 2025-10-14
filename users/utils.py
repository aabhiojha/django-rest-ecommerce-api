import uuid

def generate_otp():
    otp = str(uuid.uuid4()).split("-")[0].upper()
    return otp
