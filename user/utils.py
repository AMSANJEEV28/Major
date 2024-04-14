# user/utils.py

from .models import CustomUser

def profile_not_created(user):
    return not hasattr(user, 'userprofile')

import random
import string
from datetime import datetime, timedelta

# Function to generate OTP
def generate_otp(length=4):
    otp = ''.join(random.choices(string.digits, k=length))
    now = datetime.now()
    expiration_time = now + timedelta(minutes=2)  # Assuming OTP_EXPIRATION_MINUTES is 2 minutes
    return otp, expiration_time
