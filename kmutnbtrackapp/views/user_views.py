"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""
import datetime

from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from kmutnbtrackapp.models import *
from kmutnbtrackapp.views.help import tz, compare_current_time


def home(request):
    if request.GET:
        lab_hash = request.GET.get('next')
        if not request.user.is_authenticated:  # check if user do not login
            return HttpResponseRedirect(reverse("kmutnbtrackapp:login", args=(lab_hash,)))
        return HttpResponseRedirect(reverse("kmutnbtrackapp:lab_home", args=(lab_hash,)))
    return HttpResponse('Waiting for beautiful homepage....')


def lab_home_page(request, lab_hash):  # this function is used when user get in home page
    if not Lab.objects.filter(hash=lab_hash).exists():  # lab does not exists
        error_message = "QR code ไม่ถูกต้อง"
        return render(request, 'Page/error.html', {"error_message": error_message})

    this_lab = Lab.objects.get(hash=lab_hash)

    if not request.user.is_authenticated:  # if user hasn't login
        lab_name = this_lab.name
        return render(request, 'Page/log_in.html', {"lab_name": lab_name, "lab_hash": lab_hash})
        # render page for logging in in that lab
    else:  # if user already login
        person = Person.objects.get(user=request.user)
        now_datetime = datetime.datetime.now(tz)

        if History.objects.filter(person=person,
                                  checkin__lte=now_datetime,
                                  checkout__gte=now_datetime).exists():  # if have lastest history which checkout not at time
            last_lab_hist = History.objects.filter(person=person, checkin__lte=now_datetime, checkout__gte=now_datetime)
            last_lab_hist = last_lab_hist[0]

            if last_lab_hist.lab.hash == lab_hash:  # if latest lab is same as the going lab
                return render(request, 'Page/check_out_before_due_new.html', {"last_lab": last_lab_hist.lab})

            else:  # if latest lab is another lab
                return render(request, 'Page/lab_checkout.html', {"last_lab": last_lab_hist.lab,
                                                                  "new_lab": this_lab})

        else:  # goto checkin page
            time_option = compare_current_time()
            midnight_time = now_datetime.replace(hour=23, minute=59, second=59, microsecond=0)
            current_people = History.objects.filter(lab=this_lab,
                                                    checkout__gte=now_datetime,
                                                    checkout__lte=midnight_time).count()
            return render(request, 'Page/lab_checkin_new.html', {"lab_name": this_lab.name,
                                                                 "lab_hash": this_lab.hash,
                                                                 "time_option": time_option,
                                                                 "time_now_hour": now_datetime.hour,
                                                                 "time_now_minute": now_datetime.minute + 5,
                                                                 "current_people": current_people
                                                                 })  # render page for checkin


def username_check_api(request):
    username = request.GET.get('username')
    if User.objects.filter(username=username).count() == 0:
        return JsonResponse({"status": "available"})
    else:
        return JsonResponse({"status": "already_taken"})


def signup_api(request):  # when stranger click 'Signup and Checkin'
    if request.method == "GET":
        lab_hash = request.GET.get('next', '')
        lab_name = Lab.objects.get(hash=lab_hash).name
        return render(request, 'Page/signup_form.html', {'lab_hash': lab_hash, 'lab_name': lab_name})
    # Receive data from POST
    if request.method == "POST":
        lab_hash = request.POST.get('next', '')
        lab_name = Lab.objects.get(hash=lab_hash).name
        username = request.POST["username"]
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['rePassword']
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        # Form is valid
        if password != password_confirm:
            return render(request, 'Page/signup_form.html', {'lab_hash': lab_hash, 'lab_name': lab_name, 'wrong': 1})
        elif User.objects.filter(username=username).count() != 0:  # if username is not available
            return render(request, 'Page/signup_form.html', {'lab_hash': lab_hash, 'lab_name': lab_name, 'wrong': 2})
        elif User.objects.filter(username=username).count() == 0:  # if username is available
            # create new User object and save it
            u = User.objects.create(username=username, email=email, first_name=first_name, last_name=last_name)
            u.set_password(password)  # bypassing Django password format check
            u.save()
            # create new Person object
            Person.objects.create(user=u, first_name=first_name, last_name=last_name, email=email, is_student=False)
            # then login
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')

            return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))


def login_api(request):  # api when stranger login

    if request.method == "GET":
        if not request.user.is_authenticated:  # if user hasn't login
            lab_hash = request.GET.get('next', '')
            lab_name = ''
            if lab_hash != '':
                lab_name = Lab.objects.get(hash=lab_hash).name
            return render(request, 'Page/log_in.html', {'lab_hash': lab_hash, 'lab_name': lab_name})
        else:
            return HttpResponseRedirect("/")

    if request.method == "POST":
        lab_hash = request.GET.get('next', '')
        lab_name = ''
        if lab_hash != '':
            lab_name = Lab.objects.get(hash=lab_hash).name
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # auth username and password
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))
        else:
            return render(request, 'Page/log_in.html', {'lab_hash': lab_hash, 'lab_name': lab_name, 'wrong': 1})


def logout_api(request):  # api for logging out
    logout(request)
    try:
        lab_hash = request.GET.get("lab")
        return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))
    except:
        return HttpResponseRedirect("/")


def check_in(request, lab_hash):  # when user checkin record in history
    person = Person.objects.get(user=request.user)
    this_lab = Lab.objects.get(hash=lab_hash)

    if request.method == "POST":
        checkout_time_str = request.POST.get('check_out_time')  # get check out time
        now_datetime = datetime.datetime.now(tz)

        checkout_datetime = now_datetime.replace(hour=int(checkout_time_str.split(":")[0]),
                                                 minute=int(checkout_time_str.split(":")[
                                                                1]))  # get check out time in object datetime
        if Lab.objects.filter(hash=lab_hash).exists():  # check that lab does exists
            last_lab_hist = History.objects.filter(person=person, checkin__lte=now_datetime, checkout__gte=now_datetime)
            if last_lab_hist.exists():  # if have a history that intersect between now
                if last_lab_hist[0].lab.hash != lab_hash:  # ไปแลปอื่นแล้วแล็ปเดิมยังไม่ check out
                    return render(request, 'Page/lab_checkout.html', {"lab_hash_check_out": last_lab_hist[0].lab,
                                                                      "new_lab": this_lab})
                else:  # มาแลปเดิมแล้วถ้าจะ check in ซ้ำจะเลือกให้ check out ก่อนเวลา
                    last_hist = History.objects.get(person=person, lab=this_lab, checkin__lte=now_datetime,
                                                    checkout__gte=now_datetime)
                    return render(request, 'Page/check_out_before_due_new.html', {"last_lab": last_hist.lab})

            else:
                new_hist = History.objects.create(person=person,
                                                  lab=this_lab,
                                                  checkin=now_datetime,
                                                  checkout=checkout_datetime)

                return render(request, 'Page/lab_checkin_successful_new.html',
                              {"lab_hash": this_lab.hash,
                               "lab_name": this_lab.name,
                               "check_in": new_hist.checkin.astimezone(tz).strftime("%A, %d %B %Y, %H:%M"),
                               "check_out": new_hist.checkout.astimezone(tz).strftime("%A, %d %B %Y, %H:%M")})
    else:
        error_message = "เซสชั่นหมดอายุ กรุณาสแกน QR Code ใหม่อีกครั้ง"
        return render(request, 'Page/error.html', {"error_message": error_message, "this_lab": this_lab})


def check_out(request, lab_hash):  # api
    person = Person.objects.get(user=request.user)
    out_local_time = datetime.datetime.now(tz)
    log = History.objects.filter(person=person, lab__hash=lab_hash).order_by('checkin').last()
    log.checkout = out_local_time
    log.save()
    if request.GET.get('next_lab'):
        return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(request.GET['next_lab'],)))
    return render(request, 'Page/check_out_success.html', {"lab_name": log.lab.name})
