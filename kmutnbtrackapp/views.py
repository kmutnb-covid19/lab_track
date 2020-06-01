"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""
import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import logout, authenticate, login

from kmutnbtrackapp.models import *
from kmutnbtrackapp.forms import SignUpForm


# Create your views here.

def signup(request):
    lab_name = request.GET.get('next')
    # Receive data from POST
    if request.method == "POST":
        form = SignUpForm(request.POST)
        # Form is valid
        if form.is_valid():
            # create new user object and save it
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            # authenticate user then login
            login(request, authenticate(username=username, password=password))
            # Save user's value into Person object
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            Person.objects.create(user=user, first_name=first_name, last_name=last_name, email=email,
                                  is_student=False)
            return HttpResponseRedirect(reverse('kmutnbtrackapp:login', args=(lab_name,)))
    # didn't receive POST
    else:
        form = SignUpForm()
    return render(request, 'Page/signup.html', {'form': form})


def login_page(request, room_name):  # this function is used when user get in home page
    if not request.user.is_authenticated:
        return render(request, 'Page/check_in.html', {"room_name": room_name})
    elif Person.objects.get(user=request.user).check_in_status == 1:
        return HttpResponseRedirect(reverse("kmutnbtrackapp:check_in", args=(room_name,)))
    else:
        return render(request, 'home.html', {"room_name": room_name})


def home(request):
    if request.GET:
        lab_name = request.GET.get('next')
        amount = Lab.objects.get(name=lab_name)
        if not request.user.is_authenticated:  # check if user do not login
            return HttpResponseRedirect(reverse("kmutnbtrackapp:login", args=(lab_name,)))
        print(lab_name)
        return render(request, 'home.html', {"room_name": lab_name, 'room_amount': amount})
    else:
        error_message = "กรุณาสเเกน QR code หน้าห้อง หรือติดต่ออาจารย์ผู้สอน"
        return render(request, 'home.html', {"error_message": error_message})


def check_in(request, lab_name):  # api
    person = Person.objects.get(user=request.user)
    if Person.objects.get(user=request.user).check_in_status:  # user try to check in but he forget to check out
        lab_name = History.objects.get(person=person, checkout=None).lab.name
        return render(request, 'home.html',
                      {"check_in_status": Person.objects.get(user=request.user).check_in_status,
                       "room": lab_name})
    elif Lab.objects.filter(name=lab_name).exists():  # check that lab does exists
        lab_obj = Lab.objects.get(name=lab_name)
        person.check_in_status = True
        person.save()
        log = History.objects.create(person=person, lab=lab_obj)
        log.checkin = datetime.datetime.now()
        log.save()
        return render(request, 'home.html', {"room_check_in": lab_name, "localtime": log.checkin})
    else:  # lab does not exists
        error_message = "QR code ไม่ถูกต้อง"
        return render(request, 'home.html', {"error_message": error_message})


def check_out(request, lab_name):  # api
    person = Person.objects.get(user=request.user)
    lab_obj = Lab.objects.get(name=lab_name)
    out_local_time = datetime.datetime.now()
    log = History.objects.get(person=person, lab=lab_obj, checkout=None)
    person.check_in_status = False
    person.save()
    if not log.checkout:
        log.checkout = out_local_time
        log.save()
    logout(request)
    return render(request, 'Page/check_out_success.html', {"localtime": log.checkout, "room_check_in": lab_name})
