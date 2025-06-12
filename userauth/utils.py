import random
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage

def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(user, otp):
    subject = "Verify Your Email"
    message = f"Hello {user.first_name},\n\nYour OTP is: {otp}\n\nThis code will expire in 10 minutes. \n\nThanks, Neura Team"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    # ALSO print OTP to terminal for dev convenience
    print(f"OTP for {user.email}: {otp}")


def send_password_reset_email(email, reset_link):
    subject = "Reset Your Password"
    body = f"""
    Hi there,

    We received a request to reset your password. Click the link below to reset it:

    {reset_link}

    If you didn't request this, just ignore this email.

    Thanks,
    Neura Team
    """

    email_message = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    email_message.send(fail_silently=False)  


