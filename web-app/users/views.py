from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import Http404

from datetime import datetime
from .models import User, Ride, Vehicle

from .tools import get_verify_user, get_ride, encrypt_password, query_ride_complete, query_ride_incomplete, query_drive_complete, query_drive_incomplete, send_email, check_encrypted_password

# Create your views here.


def user_detail(request, user_id):
    user = get_verify_user(request, user_id)
    if user is not None:
        if user.isDriver:
            vehicle = list(user.vehicle.all())[0]
        else:
            vehicle = "no vehicle available"
        ride_complete = query_ride_complete(user)
        ride_incomplete = query_ride_incomplete(user)
        drive_complete = query_drive_complete(user)
        drive_incomplete = query_drive_incomplete(user)
        context = {
            "user": user,
            "vehicle": vehicle,
            "ride_complete": ride_complete,
            "ride_incomplete": ride_incomplete,
            "drive_complete": drive_complete,
            "drive_incomplete": drive_incomplete
        }
        return render(request, "users/user_detail.html", context)
    else:
        # not login, redirect to login page
        return redirect(reverse("root"))


def edit_info(request, user_id):
    user = get_verify_user(request, user_id)
    context = {}
    if user.isDriver:
        vehicle = list(user.vehicle.all())[0]
    else:
        vehicle = None
    context["user"] = user
    context["vehicle"] = vehicle
    if user is not None:
        if request.method == "POST":
            name = request.POST["username"]
            email = request.POST["email"]
            pwd_old = request.POST["password_old"]
            pwd_new = request.POST["password_new"]
            if user.isDriver:
                v_type = request.POST["type"]
                l_num = request.POST["license_number"]
                m_num = request.POST["max_num"]
                comment = request.POST["comment"]
            # make sure the email is identical
            if email != user.email:
                try:
                    User.objects.get(email=email)
                    context["error_message"] = "email has been used"
                except User.DoesNotExist:
                    user.email = email
            user.username = name
            if pwd_new != "" and \
               check_encrypted_password(pwd_old, user.password):
                user.password = encrypt_password(pwd_new)
            else:
                context["error_message"] = "password mismatch!!!"
                return render(request, "users/info_edit.html", context)
            if user.isDriver:
                vehicle = list(user.vehicle.all())[0]
                vehicle.v_type = v_type
                vehicle.license_number = l_num
                vehicle.max_number = m_num
                vehicle.comment = comment
                vehicle.save()
            user.save()
            return redirect(reverse("users:detail", args=(user.id, )))
        else:
            # GET
            return render(request, "users/info_edit.html", context)

    else:
        # not login, redirect to login page
        return redirect(reverse("root"))


def driver_signup(request, user_id):
    user = get_verify_user(request, user_id)
    if user is not None:
        if request.method == "POST":
            v_type = request.POST["type"]
            license_num = request.POST["license_number"]
            max_num = request.POST["max_num"]
            comment = request.POST["comment"]
            if comment:
                comment = ""
            user.isDriver = True
            user.vehicle.create(v_type=v_type,
                                license_number=license_num,
                                max_number=max_num,
                                comment=comment)
            user.save()
            return redirect(reverse("users:detail", args=(user.id, )))
        else:
            context = {"user": user}
            return render(request, "users/driver_signup.html", context)
    else:
        # not login, redirect to login page
        return redirect(reverse("root"))


def driver_signout(request, user_id):
    user = get_verify_user(request, user_id)
    if user is not None:
        if user.isDriver:
            user.vehicle.all().delete()
            user.isDriver = False
            user.save()
        return redirect(reverse("users:detail", args=(user.id, )))
    else:
        # not login, redirect to login page
        return redirect(reverse("root"))


def ride_detail(request, user_id, ride_id):
    user = get_verify_user(request, user_id)
    ride = get_ride(request, ride_id)
    context = {"user": user, "ride": ride, "error_message": ""}
    if ride.driver_id != -1:
        u = User.objects.get(pk=ride.driver_id)
        context["driver_name"] = u.username
    context["ediable"] = ride.owner == user and ride.status == "open" and len(
        ride.sharer.all()) == 0
    if request.method == "POST":
        operation = request.POST["operation"]
        if operation == "share":
            new_num = request.POST["new_num"]
            ride = Ride.objects.get(id=ride_id)
            result, info = verify_sharable(ride, user, int(new_num))
            if result:
                # statisfy share condition
                ride.sharer.add(user)
                ride.passenger_num = ride.passenger_num + int(new_num)
                ride.save()
                return redirect(reverse("homepage", args=(user.username, )))
            else:
                context["error_message"] = info
        elif operation == "confirm":
            vehicle = list(user.vehicle.all())[0]
            if ride.status == "open" and ride.owner.id != user_id \
               and vehicle.max_number >= ride.passenger_num:
                ride.driver_id = user_id
                ride.status = "confirmed"
                ride.save()
                text = "Your ride has been confirmed\n" + \
                       "Destination: " + ride.destination + "\n" + \
                       "Time: " + ride.get_date_str() + \
                       "  " + ride.get_time_str() + "\n" + \
                       "Passenger Numbers: " + str(ride.passenger_num) + "\n"
                emails = [e.email for e in ride.sharer.all()]
                emails.append(ride.owner.email)
                send_email(emails, text)
                context = {"user": user, "ride": ride}
                return render(request, "users/confirm_ride.html", context)
            else:
                context["error_message"] = "you can't confirm this ride"
        else:
            # complete current ride
            if ride.status == "confirmed" and ride.driver_id == user_id:
                ride.status = "complete"
                ride.save()
                context = {"user": user, "ride": ride}
                return render(request, "users/complete_ride.html", context)
            else:
                context["error_message"] = "you can't complete this ride"
    return render(request, "users/ride_detail.html", context)


# driver confirms a ride
def confirm_ride(request, user_id, ride_id):
    user = get_verify_user(request, user_id)
    ride = get_ride(request, ride_id)
    context = {"user": user, "ride": ride}
    return render(request, "users/confirm_ride.html", context)


# driver completes a ride
def complete_ride(request, user_id, ride_id):
    user = get_verify_user(request, user_id)
    ride = get_ride(request, ride_id)
    context = {"user": user, "ride": ride}
    return render(request, "users/complete_ride.html", context)


# ride confirm(share or request)
def ride_confirm(request, user_id, ride_id):
    user = get_verify_user(request, user_id)
    context = {}
    if request.method == "POST":
        dest = request.POST["destination"]
        date = request.POST["date"]
        time = request.POST["time"]
        num = request.POST["numbers"]
        canShare = request.POST.__contains__("canShare")
        vehicle = request.POST["vehicle"]
        comment = request.POST["comment"]
        ride = Ride(destination=dest,
                    date=datetime.strptime(date, "%Y-%m-%d"),
                    time=datetime.strptime(time, "%H:%M"),
                    passenger_num=int(num),
                    vehicle=vehicle,
                    canShare=canShare,
                    special_info=comment)
        success, info = add_edit_ride(request, user, ride, ride_id)
        if success:
            if ride_id == 0:
                # go back to homepage(add request will call add ride)
                return redirect(reverse("homepage", args=(user.username, )))
            else:
                # go back to user detail page
                return redirect(reverse("users:detail", args=(user.id, )))
        else:
            context["error_message"] = info
    else:
        if ride_id == 0:
            ride = Ride(destination="",
                        date=datetime.date(datetime.now()),
                        time=datetime.time(datetime.now()),
                        passenger_num=1,
                        vehicle="CarX",
                        canShare=False,
                        special_info="")
        else:
            ride = Ride.objects.get(pk=ride_id)
    context["ride"] = ride
    context["ride_id"] = ride_id
    context["user"] = user
    return render(request, "users/ride_confirm.html", context)


def add_edit_ride(request, user, ride, ride_id):
    valid, info = request_validate(ride.destination, ride.date, ride.time,
                                   ride.passenger_num)
    if valid:
        # current request data is valid
        if ride_id == 0:
            # add ride
            user.ride_own.create(destination=ride.destination,
                                 date=ride.date,
                                 time=ride.time,
                                 canShare=ride.canShare,
                                 passenger_num=ride.passenger_num,
                                 vehicle=ride.vehicle,
                                 special_info=ride.special_info)
            return True, ""
        else:
            # edit ride
            r = Ride.objects.get(pk=ride_id)
            r.destination = ride.destination
            r.date = ride.date
            r.time = ride.time
            r.passenger_num = ride.passenger_num
            r.canShare = ride.canShare
            r.vehicle = ride.vehicle
            r.special_info = ride.special_info
            r.save()
            return True, ""
    else:
        # invalid request data
        return False, info


def request_validate(dest, date, time, num):
    if dest == "":
        return False, "FAILED: destination can't be empty!!!"
    if num > 8:
        return False, "FAILED: too many people to fit in one car!!!"
    if datetime.date(date) < datetime.date(datetime.now()) or (
            datetime.date(date) == datetime.date(datetime.now())
            and datetime.time(time) < datetime.time(datetime.now())):
        return False, "FAILED: datetime is in the past, invalid!!!"
    return True, ""


def verify_sharable(ride, user, num):
    left = ride.get_left_cap()
    if left < num:
        return False, "FAILED: not enough room for " + str(
            num) + " more people"
    elif ride.owner == user:
        return False, "FAILED: owner can't share his own ride"
    elif user in ride.sharer.all():
        return False, "FAILED: you already are the sharer of current ride"
    else:
        return True, ""
