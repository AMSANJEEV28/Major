from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout, authenticate
from .forms import SignUpForm, SignInForm, UserProfileForm
from .models import CustomUser
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string
from allauth.socialaccount.models import SocialAccount

# Function to check if the user profile is not created
def profile_not_created(user):
    return not hasattr(user, 'userprofile')

# Define the expiration time for the OTP (in minutes)
OTP_EXPIRATION_MINUTES = 2

# Function to generate OTP
def generate_otp(length=4):
    otp = ''.join(random.choices(string.digits, k=length))
    # Get the current time
    now = datetime.now()
    # Calculate the expiration time by adding OTP_EXPIRATION_MINUTES to the current time
    expiration_time = now + timedelta(minutes=OTP_EXPIRATION_MINUTES)
    # Return the OTP and its expiration time as a tuple
    return otp, expiration_time

from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import UserProfile


# Signin view
def signin(request):
    if request.user.is_authenticated:
        # If the user is already authenticated, redirect to the profile page
        return redirect('user:profile')

    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Authenticate user using email as the username
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)

                if profile_not_created(user):
                    return redirect('user:create_profile')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
        else:
            messages.error(request, 'There was an error with your signin. Please correct the errors below.')
    else:
        form = SignInForm()

    return render(request, 'signin.html', {'form': form})

# Edit profile view
@login_required
def edit_profile(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            # Redirect to another page after successful form submission
            return redirect('home')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'create_profile.html', {'form': form})


from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm, UserProfileForm
from .models import CustomUser, UserProfile
from datetime import datetime

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            existing_user = CustomUser.objects.filter(email=email).first()
            if existing_user:
                messages.info(request, 'An account with this email already exists. Please sign in.')
                return redirect('user:signin')
            else:
                otp, expiration_time = generate_otp()

                request.session['otp'] = otp
                request.session['otp_expiration_time'] = expiration_time.strftime("%Y-%m-%d %H:%M:%S")
                request.session['email'] = email

                subject = 'Your OTP for Account Verification'
                message = f'Your OTP is: {otp}. Please use this OTP to sign up on College Connect website.'
                sender_email = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail(subject, message, sender_email, recipient_list)

                return redirect('user:verify_otp')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm, UserProfileForm
from .models import CustomUser, UserProfile
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserProfileForm
from .models import UserProfile, CustomUser
from datetime import datetime

# def verify_otp(request):
#     if request.method == 'POST':
#         otp_entered = request.POST.get('otp', '')
#         otp_saved = request.session.get('otp', '')
#         expiration_time_str = request.session.get('otp_expiration_time', '')

#         if expiration_time_str:
#             expiration_time = datetime.strptime(expiration_time_str, "%Y-%m-%d %H:%M:%S")
#             current_time = datetime.now()

#             if current_time > expiration_time:
#                 messages.error(request, 'OTP has expired. Please request a new OTP.')
#                 return redirect('user:signup')  # Redirect to signup page if OTP is expired

#         if otp_entered == otp_saved:
#             # OTP is valid, perform account creation and login
#             email = request.session.get('email', '')

#             # Create user account if not exists
#             user, created = CustomUser.objects.get_or_create(email=email)
#             if created:
#                 # Set username to email
#                 user.username = email
#                 user.save()

#             # Log the user in
#             login(request, user, backend='django.contrib.auth.backends.ModelBackend')

#             return redirect('user:create_profile')  # Redirect to create profile page if profile is not created
#         else:
#             messages.error(request, 'Invalid OTP. Please try again.')

#     return render(request, 'otp.html', {'otp_expired': False})


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserProfileForm
from .models import CustomUser, UserProfile
from datetime import datetime

def verify_otp(request):
    if request.method == 'POST':
        otp_entered = (
            request.POST.get('otp1', '') +
            request.POST.get('otp2', '') +
            request.POST.get('otp3', '') +
            request.POST.get('otp4', '')
        )

        otp_saved = request.session.get('otp', '')
        expiration_time_str = request.session.get('otp_expiration_time', '')

        print(f"Entered OTP: {otp_entered}")
        print(f"Saved OTP: {otp_saved}")
        print(f"Expiration Time String: {expiration_time_str}")

        if expiration_time_str:
            expiration_time = datetime.strptime(expiration_time_str, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()

            if current_time > expiration_time:
                messages.error(request, 'OTP has expired. Please request a new OTP.')
                print("OTP Expired")
                return redirect('user:signup')  # Redirect to signup page if OTP is expired

        if otp_entered == otp_saved:
            # OTP is valid, perform account creation and login
            email = request.session.get('email', '')

            # Create user account if not exists
            user, created = CustomUser.objects.get_or_create(email=email)
            if created:
                # Set username to email
                user.username = email
                user.save()

            # Log the user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            print("OTP Verified Successfully")
            return redirect('user:create_profile')  # Redirect to create profile page if profile is not created
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            print("Invalid OTP Entered")

    return render(request, 'otp.html', {'otp_expired': False})


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserProfileForm
from .models import UserProfile
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserProfileForm
from .models import University, College
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserProfileForm
from .models import UserProfile

def create_profile(request):
    # Check if the profile already exists for the user
    try:
        profile = request.user.userprofile  # Retrieve the user's profile if it exists
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('home')  # Redirect to home after profile update
        else:
            messages.error(request, 'There was an error with your profile update. Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'create_profile.html', {'form': form})


# Profile view
@login_required
def profile(request):
    user_profile = request.user.userprofile
    user_email = request.user.email  # Accessing the email from CustomUser model
    return render(request, 'profile.html', {'user_profile': user_profile, 'user_email': user_email})

# Signout view
def signout(request):
    logout(request)
    return redirect('home')



