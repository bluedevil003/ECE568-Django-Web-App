import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from passlib.context import CryptContext

from django.shortcuts import get_object_or_404
from .models import User, Ride

# email address info
SMTP_SERVER = 'smtp.gmail.com:587'
USER_ACCOUNT = {
    'username': 'ece568noreply@gmail.com',
    'password': 'ece568code'
}

# encryption info
pwd_context = CryptContext(schemes=["pbkdf2_sha256"],
                           default="pbkdf2_sha256",
                           pbkdf2_sha256__default_rounds=30000)


def send_email(receivers, text):
    msg_root = MIMEMultipart()
    msg_root['Subject'] = "Info from MyLyft568"
    msg_root['To'] = ", ".join(receivers)
    msg_text = MIMEText(text)
    msg_root.attach(msg_text)

    smtp = smtplib.SMTP(SMTP_SERVER)
    smtp.starttls()
    smtp.login(USER_ACCOUNT["username"], USER_ACCOUNT["password"])
    smtp.sendmail(USER_ACCOUNT["username"], receivers, msg_root.as_string())
    smtp.quit()


def get_verify_user(request, user_id):
    email = request.session.get("email", "")
    user = get_object_or_404(User, pk=user_id)
    if user.email == email:
        return user
    else:
        return None


def query_ride_incomplete(user):
    a = list(user.ride_own.exclude(status="complete").all())
    b = list(user.ride_share.exclude(status="complete").all())
    a.extend(b)
    return a


def query_ride_complete(user):
    a = list(
        user.ride_own.exclude(status="open").exclude(status="confirmed").all())
    b = list(
        user.ride_share.exclude(status="open").exclude(
            status="confirmed").all())
    a.extend(b)
    return a


def query_drive_complete(user):
    return Ride.objects.exclude(status="confirmed").filter(
        driver_id=user.id).all()


def query_drive_incomplete(user):
    return Ride.objects.exclude(status="complete").filter(
        driver_id=user.id).all()


def get_ride(request, ride_id):
    ride = get_object_or_404(Ride, pk=ride_id)
    return ride


def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)


if __name__ == "__main__":
    text = "Your ride has been confirmed\n" + \
                       "Destination: " + "Duke" + "\n" + \
                       "Time: " + "2020-03-09" + "  " + "12:00" + "\n" + \
                       "Passenger Numbers: " + "5" + "\n"
    send_email(["xiakewei96@gmail.com"], text)
    pwd = "1030"
    hashed = encrypt_password(pwd)
    p = check_encrypted_password(pwd, hashed)
    print(pwd)
    print(hashed)
    if p:
        print("passed")
    else:
        print("failed")
