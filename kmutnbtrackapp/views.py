from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from kmutnbtrackapp.models import *
from django.template import RequestContext
import time

# Create your views here.



def login(request,room_name):#this function is used when user get in home page
    return render(request,'Page/login.html', {"room_name": room_name})

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

def checkIn(request):
    lab_name = request.GET.get('room')
    print("checkin:")
    print(lab_name)
    if Lab.objects.filter(lab_name=lab_name).exists():
        Student = StudentID.objects.get(user=request.user)
        lab_obj = Lab.objects.get(lab_name=lab_name)
        if not History.objects.filter(Student=Student,lab=lab_obj,lab_name=lab_obj.lab_name,student_name=request.user.first_name+request.user.last_name,student_ids=Student.student_id).exists():
            inlocaltime = time.asctime(time.localtime(time.time()))
            History.objects.create(Student=Student,lab=lab_obj,lab_name=lab_obj.lab_name,student_name=request.user.first_name+request.user.last_name,student_ids=Student.student_id,checkin=inlocaltime)
            return render(request, 'home.html', {"localtime": inlocaltime, "room_check_in": lab_name})
        Log=History.objects.get(Student=Student, lab=lab_obj, lab_name=lab_obj.lab_name,student_name=request.user.first_name + request.user.last_name,student_ids=Student.student_id)
        return render(request, 'home.html', {"localtime": Log.checkin, "room_check_in": lab_name})
    else:
        error_message = "QR code ไม่ถูกต้อง"
        return render(request, 'home.html', {"error_message": error_message})

def checkOut(request):
    lab_name = request.GET.get('roomout')
    Student = StudentID.objects.get(user=request.user)
    lab_obj = Lab.objects.get(lab_name=lab_name)
    outlocaltime = time.asctime(time.localtime(time.time()))
    Log=History.objects.get(Student=Student, lab=lab_obj, lab_name=lab_obj.lab_name,student_name=request.user.first_name + request.user.last_name,student_ids=Student.student_id)
    if not Log.checkout:
        Log.checkout=outlocaltime
        Log.save()
    return render(request, 'Page/logout_success.html', {"localtime": Log.checkout, "room_check_in": lab_name})
