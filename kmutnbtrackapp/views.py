from django.shortcuts import render
import time

# Create your views here.


def login(request,room_name):#this function is used when user get in home page
    return render(request,'Page/login.html', {"room_name": room_name})

def home(request):
    if request.GET:
        room_name = request.GET.get('next')
        print(room_name)
        return render(request,'home.html',{"room_name":room_name})
    else:
        error_message = "กรุณาสเเกน QR code หน้าห้อง หรือติดต่ออาจารย์ผู้สอน"
        return render(request, 'home.html', {"error_message": error_message})

def checkIn(request):
    room_check_in = request.GET.get('room')
    localtime = time.asctime(time.localtime(time.time()))
    print(room_check_in)
    print("เวลา Check in :", localtime)

    return render(request, 'home.html', {"localtime": localtime,"room_check_in":room_check_in})