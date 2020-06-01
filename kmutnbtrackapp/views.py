import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from kmutnbtrackapp.models import *
from django.template import RequestContext
import time

# Create your views here.


def login(request,room_name):#this function is used when user login
    if not request.user.is_authenticated:#user do not login
        return render(request, 'Page/login.html', {"room_name": room_name})
    person=Person.objects.get(user=request.user)
    if Person.objects.get(user=request.user).check_in_status :#user does not check out go to line 40
        lab_name = History.objects.get(person=person, checkout=None).lab.name
        return HttpResponseRedirect(reverse("kmutnbtrackapp:check_in",args=[lab_name]))
    else:#user can check in
        return render(request, 'home.html', {"room_name": room_name})


def home(request):
    if request.GET:
        lab_name = request.GET.get('next')
        if not request.user.is_authenticated:#check if user do not login
            return HttpResponseRedirect(reverse("kmutnbtrackapp:login",args=[lab_name]))
        print(lab_name)
        return render(request,'home.html',{"room_name":lab_name})
    else:
        error_message = "กรุณาสเเกน QR code หน้าห้อง หรือติดต่ออาจารย์ผู้สอน"
        return render(request, 'home.html', {"error_message": error_message})


def checkIn(request,lab_name):
    person = Person.objects.get(user=request.user)
    if Person.objects.get(user=request.user).check_in_status:#user try to check in but he forget to check out
        lab_name=History.objects.get(person=person,checkout=None).lab.name
        return render(request, 'home.html',
                          {"check_in_status": Person.objects.get(user=request.user).check_in_status,
                           "room": lab_name})
    elif Lab.objects.filter(name=lab_name).exists():#check that lab does exists
        lab_obj = Lab.objects.get(name=lab_name)
        person.check_in_status = True
        person.save()
        Log = History.objects.create(person=person,lab=lab_obj)
        Log.checkin = datetime.datetime.now()
        Log.save()
        return render(request, 'home.html', {"room_check_in": lab_name,"localtime":Log.checkin})
    else:# lab does not exists
        error_message = "QR code ไม่ถูกต้อง"
        return render(request, 'home.html', {"error_message": error_message})


def checkOut(request,lab_name): #api
    person = Person.objects.get(user=request.user)
    lab_obj = Lab.objects.get(name=lab_name)
    out_local_time = datetime.datetime.now()
    Log=History.objects.get(person=person,lab=lab_obj,checkout=None)
    person.check_in_status = False
    person.save()
    if not Log.checkout:
        Log.checkout=out_local_time
        Log.save()
    return render(request, 'Page/logout_success.html', {"localtime": Log.checkout, "room_check_in": lab_name})
