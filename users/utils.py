import uuid

def create_otp(self):
    otp = str(uuid.uuid4()).split("-")[0].upper()
    return otp
