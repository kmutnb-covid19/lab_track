"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""
import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.urls import reverse
from django.contrib.auth import logout

from kmutnbtrackapp.models import *


# Create your views here.

def login(request, room_name):  # this function is used when user get in home page
    if not request.user.is_authenticated:
        return render(request, 'Page/login.html', {"room_name": room_name})
    elif Person.objects.get(user=request.user).check_in_status == 1:
        return HttpResponseRedirect(reverse("kmutnbtrackapp:check_in"))
    else:
        return render(request, 'home.html', {"room_name": room_name})


def home(request):
    if request.GET:
        lab_name = request.GET.get('next')
        amount = Lab.objects.get(name=lab_name)
        if not request.user.is_authenticated:  # check if user do not login
            return HttpResponseRedirect(reverse("kmutnbtrackapp:login", args=[lab_name]))
        print(lab_name)
        return render(request, 'home.html', {"room_name": lab_name, 'room_amount': amount})
    else:
        error_message = "กรุณาสเเกน QR code หน้าห้อง หรือติดต่ออาจารย์ผู้สอน"
        return render(request, 'home.html', {"error_message": error_message})


def check_in(request):  # api
    person = Person.objects.get(user=request.user)
    if Person.objects.get(user=request.user).check_in_status:
        lab_name = History.objects.get(person=person, checkout=None).lab.name
    else:
        lab_name = request.GET.get('room')
    in_local_time = datetime.datetime.now()
    if Lab.objects.filter(name=lab_name).exists():
        lab_obj = Lab.objects.get(name=lab_name)
        if not History.objects.filter(person=person, lab=lab_obj).exists():
            person.check_in_status = True
            person.save()
            History.objects.create(person=person, lab=lab_obj, checkin=in_local_time)
            log = History.objects.get(person=person, lab=lab_obj)
            return render(request, 'home.html', {"localtime": log.checkin, "room_check_in": lab_name})
        log = History.objects.get(person=person, lab=lab_obj)
        return render(request, 'home.html', {"localtime": log.checkin, "room_check_in": lab_name})
    else:
        error_message = "QR code ไม่ถูกต้อง"
        return render(request, 'home.html', {"error_message": error_message})


def check_out(request):  # api
    lab_name = request.GET.get('roomout')
    person = Person.objects.get(user=request.user)
    lab_obj = Lab.objects.get(name=lab_name)
    out_local_time = datetime.datetime.now()
    log = History.objects.get(person=person, lab=lab_obj)
    person.check_in_status = False
    person.save()
    if not log.checkout:
        log.checkout = out_local_time
        log.save()
    logout(request)

    return render(request, 'Page/logout_success.html', {"localtime": log.checkout.strftime("%A, %d %B %Y, %H:%M:%S"),
                                                        "room_check_in": lab_name})
