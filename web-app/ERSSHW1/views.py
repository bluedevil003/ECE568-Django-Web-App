from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.db.models import Q
from datetime import datetime, timedelta
from users.models import User, Ride, Vehicle
from users.tools import encrypt_password, check_encrypted_password


def root(request):
    context = {"hello": "Welcome to our first ECE568 HW!!!"}
    return render(request, "login.html", context)


def login(request):
    context = {}
    context["hello"] = "Welcome to our first ECE568 HW!!!"
    if request.method == 'POST':
        name = request.POST["username"]
        email = request.POST["email"]
        pwd = request.POST["password"]
        try:
            user = User.objects.get(email=email)
            if user.username == name and check_encrypted_password(
                    pwd, user.password):
                request.session["email"] = email
                return redirect(
                    reverse("homepage", kwargs={'user_name': user.username}))
            else:
                context["result"] = "Invalid username or password!!!"
        except User.DoesNotExist:
            context["result"] = "Invalid username or password!!!"
    else:
        raise Http404("Use POST method please!!!")

    return render(request, "login.html", context)


def logout(request):
    try:
        del request.session["email"]
    except KeyError:
        pass
    return redirect(reverse("root"))


def signup(request):
    if request.method == 'POST':
        name = request.POST["username"]
        email = request.POST["email"]
        pwd = request.POST["password"]
        try:
            User.objects.get(email=email)
            # user already exist
            context = {
                "hello": "Welcome to our first ECE568 HW1!!!",
                "error_message": "user already exist"
            }
            return render(request, "signup.html", context)
        except User.DoesNotExist:
            # new user
            User(username=name,
                 email=email,
                 password=encrypt_password(pwd),
                 isDriver=False).save()
            return redirect(reverse("root"))
    elif request.method == 'GET':
        context = {"hello": "Welcome to our first ECE568 HW!!!"}
        return render(request, "signup.html", context)


def home(request, user_name):
    email = request.session.get("email", "")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Http404("user does not exist")

    if user.username == user_name:
        context = {}
        context["user"] = user
        if request.method == "POST":
            # search button
            context["debug_info"] = "method: POST\n"
            dst = request.POST["destination"]
            num = request.POST["numbers"]
            sdate = request.POST["sdate"]
            stime = request.POST["stime"]
            edate = request.POST["edate"]
            etime = request.POST["etime"]
            ride_list = search_ride(user, dst, int(num), sdate, stime, edate,
                                    etime)
        else:
            context["debug_info"] = "method: GET\n"
            dst = ""
            num = 0
            date_format = "%Y-%m-%d"
            time_format = "%H:%M"
            sdate = datetime.now().strftime(date_format)
            stime = (datetime.now() - timedelta(hours=1)).strftime(time_format)
            edate = datetime.now().strftime(date_format)
            etime = (datetime.now() + timedelta(hours=1)).strftime(time_format)
            # only show the ride which can be shared or need a driver
            if (user.isDriver):
                # show all open ride, exclude the ride current user own
                ride_list = Ride.objects.filter(status="open").exclude(
                    owner=user).all()
            else:
                # show all open ride which can be shared
                ride_list = Ride.objects.filter(
                    Q(canShare=True)
                    & Q(status="open")).exclude(owner=user).all()
            # exclude any ride current user sharing
            ride_list = [
                ride for ride in ride_list if user not in ride.sharer.all()
            ]

        context["ride_list"] = ride_list
        context["dst"] = dst
        context["num"] = num
        context["sdate"] = sdate
        context["stime"] = stime
        context["edate"] = edate
        context["etime"] = etime
        return render(request, "home.html", context)
    else:
        return redirect(reverse("root"))


""" ====== helper function ====== """


def search_ride(user, dst, num, sdate, stime, edate, etime):
    querySet = Ride.objects.exclude(owner=user).exclude(driver_id=user.id)
    if dst != "":
        querySet = querySet.filter(destination=dst)
    querySet = querySet.filter(date__gte=sdate).filter(date__lte=edate)
    querySet = querySet.exclude(Q(date=sdate) & Q(time__lte=stime))
    querySet = querySet.exclude(Q(date=edate) & Q(time__gte=etime))
    ride = [r for r in querySet.all() if r.get_left_cap() >= num]
    return ride
