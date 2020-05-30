from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import logout

from kmutnbtrackapp.models import *
import datetime


# Create your views here.


def login(request, room_name):  # this function is used when user get in home page
    return render(request, 'Page/login.html', {"room_name": room_name})


def home(request):
    if request.GET:
        lab_name = request.GET.get('next')
        if not request.user.is_authenticated:  # check if user do not login
            return HttpResponseRedirect(reverse("kmutnbtrackapp:login", args=[lab_name]))
        print(lab_name)
        return render(request, 'home.html', {"room_name": lab_name})
    else:
        error_message = "กรุณาสเเกน QR code หน้าห้อง หรือติดต่ออาจารย์ผู้สอน"
        return render(request, 'home.html', {"error_message": error_message})


def check_in(request):
    lab_name = request.GET.get('room')
    print("checkin:")
    print(lab_name)
    if Lab.objects.filter(lab_name=lab_name).exists():
        student = StudentID.objects.get(user=request.user)
        lab_obj = Lab.objects.get(lab_name=lab_name)
        if not History.objects.filter(Student=student, lab=lab_obj, lab_name=lab_obj.lab_name,
                                      student_name=request.user.first_name + " " + request.user.last_name,
                                      student_ids=student.student_id).exists():
            in_local_time = datetime.datetime.now()
            History.objects.create(Student=student, lab=lab_obj, lab_name=lab_obj.lab_name,
                                   student_name=request.user.first_name + " " + request.user.last_name,
                                   student_ids=student.student_id, checkin=in_local_time)
            return render(request, 'home.html', {"localtime": in_local_time.strftime("%A, %d %B %Y, %H:%M:%S"),
                                                 "room_check_in": lab_name})
        log = History.objects.get(Student=student, lab=lab_obj, lab_name=lab_obj.lab_name,
                                  student_name=request.user.first_name + " " + request.user.last_name,
                                  student_ids=student.student_id)
        return render(request, 'home.html', {"localtime": log.checkin.strftime("%A, %d %B %Y, %H:%M:%S"),
                                             "room_check_in": lab_name})
    else:
        error_message = "QR code ไม่ถูกต้อง"
        return render(request, 'home.html', {"error_message": error_message})


def check_out(request):
    lab_name = request.GET.get('roomout')
    student = StudentID.objects.get(user=request.user)
    lab_obj = Lab.objects.get(lab_name=lab_name)
    out_local_time = datetime.datetime.now()
    log = History.objects.get(Student=student, lab=lab_obj, lab_name=lab_obj.lab_name,
                              student_name=request.user.first_name + " " + request.user.last_name,
                              student_ids=student.student_id)
    if not log.checkout:
        log.checkout = out_local_time
        log.save()
    logout(request)

    return render(request, 'Page/logout_success.html', {"localtime": log.checkout.strftime("%A, %d %B %Y, %H:%M:%S"),
                                                        "room_check_in": lab_name})
