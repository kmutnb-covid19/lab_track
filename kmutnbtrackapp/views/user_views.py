"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""

import datetime
import re

from social_django.middleware import SocialAuthExceptionMiddleware
from social_core import exceptions as social_exceptions
from django.contrib.auth import logout, login
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from django.urls import reverse

from kmutnbtrackapp.models import *
from kmutnbtrackapp.views.help import tz, compare_current_time
from kmutnbtrackapp.forms import SignUpForm


class MySocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if hasattr(social_exceptions, exception.__class__.__name__):
            error_message = "กรุณาแสกน QR Code ใหม่อีกครั้ง และกรุณางดใช้ in-app browser เพื่อป้องกันการ error"
            return render(request, 'Page/error.html', {"error_message": error_message})
        else:
            return super(MySocialAuthExceptionMiddleware, self).process_exception(request, exception)


def home(request):
    if request.GET.get('next'):
        lab_hash = request.GET.get('next')
        if not request.user.is_authenticated:  # check if user do not login
            return HttpResponseRedirect(reverse("kmutnbtrackapp:login", args=(lab_hash,)))
        return HttpResponseRedirect(reverse("kmutnbtrackapp:lab_home", args=(lab_hash,)))
    return render(request, 'Page/homepage.html')


def lab_home_page(request, lab_hash):  # this function is used when user get in home page
    if not Lab.objects.filter(hash=lab_hash).exists():  # lab does not exists
        error_message = "QR code ไม่ถูกต้อง"
        return render(request, 'Page/error.html', {"error_message": error_message})

    this_lab = Lab.objects.get(hash=lab_hash)

    now_datetime = datetime.datetime.now(tz)
    if not request.user.is_authenticated:  # if user hasn't login
        lab_name = this_lab.name
        return render(request, 'Page/log_in.html', {"lab_name": lab_name, "lab_hash": lab_hash})
        # render page for logging in in that lab
    else:  # if user already login
        person = Person.objects.get(user=request.user)
        # if have latest history which checkout not at time
        if History.objects.filter(person=person, checkin__lte=now_datetime, checkout__gte=now_datetime).exists():
            last_lab_hist = History.objects.filter(person=person, checkin__lte=now_datetime, checkout__gte=now_datetime)
            last_lab_hist = last_lab_hist[0]

            if last_lab_hist.lab.hash == lab_hash:  # if latest lab is same as the going lab
                return render(request, 'Page/check_out_before_due_new.html',
                              {"last_lab": last_lab_hist.lab,
                               "check_in": last_lab_hist.checkin.astimezone(tz).strftime("%A, %d %b %Y, %H:%M"),
                               "check_out": last_lab_hist.checkout.astimezone(tz).strftime("%A, %d %b %Y, %H:%M")})

            else:  # if latest lab is another lab
                return render(request, 'Page/check_out_prev_lab_before.html',
                              {"last_lab": last_lab_hist.lab, "new_lab": this_lab})

        else:  # goto checkin page
            time_option = compare_current_time()
            midnight_time = now_datetime.replace(hour=23, minute=59, second=59, microsecond=0)
            current_people = History.objects.filter(lab=this_lab, checkout__gte=now_datetime,
                                                    checkout__lte=midnight_time).count()
            lab_exceeded_limit = False
            if current_people >= this_lab.max_number_of_people:
                lab_exceeded_limit = True
            return render(request, 'Page/lab_checkin_new.html', {"lab_name": this_lab.name,
                                                                 "lab_hash": this_lab.hash,
                                                                 "time_option": time_option,
                                                                 "time_now_hour": now_datetime.hour,
                                                                 "time_now_minute": now_datetime.minute + 5,
                                                                 "current_people": current_people,
                                                                 "lab_exceeded_limit": lab_exceeded_limit,
                                                                 "maximum_people": this_lab.max_number_of_people
                                                                 })  # render page for checkin


def login_api(request):  # api when stranger login
    if request.method == "GET":
        if not request.user.is_authenticated:  # if user hasn't login
            lab_name = ''
            lab_hash = request.GET.get('next', '')
            if lab_hash != '':
                lab_name = Lab.objects.get(hash=lab_hash).name
            return render(request, 'Page/log_in.html', {'lab_hash': lab_hash, 'lab_name': lab_name})
        else:
            return HttpResponseRedirect("/")

    if request.method == "POST":
        lab_hash = request.GET.get('next', '')
        tel_no = request.POST['tel']
        if User.objects.filter(username=tel_no).exists():  # if phone number already in database
            user = User.objects.get(username=tel_no)
            login(request, user,
                  backend='django.contrib.auth.backends.ModelBackend')  # login with username only
            return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))
        else:  # phone number not in database
            return HttpResponseRedirect(reverse('kmutnbtrackapp:signup', args=(lab_hash,)))


def signup_api(request, lab_hash):  # when stranger click 'Signup and Checkin'
    if request.method == "GET":
        lab_name = Lab.objects.get(hash=lab_hash).name
        return render(request, 'Page/signup_form.html', {'lab_hash': lab_hash, 'lab_name': lab_name, })

    # Receive data from POST
    if request.method == "POST":
        lab_name = Lab.objects.get(hash=lab_hash).name
        tel_no = request.POST["tel"]
        if not re.match(r"[0-9]|\.", tel_no):  # if input is not phone number
            error_message = "รูปแบบเบอร์ไม่ถูกต้อง กรุณาสแกน QR Code ใหม่อีกครั้ง"
            return render(request, 'Page/error.html', {"error_message": error_message})
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        # Form is valid
        if User.objects.filter(username=tel_no).count() != 0:  # if username is already taken
            return render(request, 'Page/signup_form.html', {'lab_hash': lab_hash, 'lab_name': lab_name, 'wrong': 2})
        else:  # if username is available
            # create new User object and save it
            u = User.objects.create(username=tel_no, first_name=first_name, last_name=last_name)
            u.save()
            # create new Person object
            Person.objects.create(user=u, first_name=first_name, last_name=last_name, is_student=False)
            # then login
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))


def logout_api(request):  # api for logging out
    logout(request)
    lab_hash = request.GET.get("lab", None)
    if lab_hash:
        return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))
    else:
        return HttpResponseRedirect("/")


def check_in(request, lab_hash):  # when user checkin record in history
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))
    person = Person.objects.get(user=request.user)
    if Lab.objects.filter(hash=lab_hash).exists():
        this_lab = Lab.objects.get(hash=lab_hash)
    else:
        error_message = "QR code ไม่ถูกต้อง"
        return render(request, 'Page/error.html', {"error_message": error_message})

    if request.method == "POST":
        checkout_time_str = request.POST['check_out_time']  # get check out time
        now_datetime = datetime.datetime.now(tz)
        midnight_time = now_datetime.replace(hour=23, minute=59, second=59, microsecond=0)

        checkout_datetime = now_datetime.replace(hour=int(checkout_time_str.split(":")[0]),
                                                 minute=int(checkout_time_str.split(":")[
                                                                1]))  # get check out time in object datetime
        if Lab.objects.filter(hash=lab_hash).exists():  # check that lab does exists
            last_lab_hist = History.objects.filter(person=person, checkin__lte=now_datetime, checkout__gte=now_datetime)
            if last_lab_hist.exists():  # if have a history that intersect between now
                if last_lab_hist[0].lab.hash != lab_hash:  # if latest lab is another lab
                    return render(request, 'Page/check_out_prev_lab_before.html',
                                  {"lab_hash_check_out": last_lab_hist[0].lab,
                                   "new_lab": this_lab})
                else:  # if latest lab is same as the going lab
                    last_lab_hist = History.objects.get(person=person, lab=this_lab, checkin__lte=now_datetime,
                                                        checkout__gte=now_datetime)
                    return render(request, 'Page/check_out_before_due_new.html',
                                  {"last_lab": last_lab_hist.lab,
                                   "check_in": last_lab_hist.checkin.astimezone(tz).strftime("%A, %d %b %Y, %H:%M"),
                                   "check_out": last_lab_hist.checkout.astimezone(tz).strftime("%A, %d %b %Y, %H:%M")})
            else:
                new_hist = History.objects.create(person=person,
                                                  lab=this_lab,
                                                  checkin=now_datetime,
                                                  checkout=checkout_datetime)
                current_people = History.objects.filter(lab=this_lab, checkout__gte=now_datetime,
                                                        checkout__lte=midnight_time).count()
                if current_people > this_lab.max_number_of_people:
                    print(current_people)
                    print(this_lab.max_number_of_people)
                    new_hist.exceeded_limit = True
                    new_hist.save()
                    if person.ask_feedback is False:
                        return render(request, 'Page/lab_checkin_successful_new.html',
                                      {"lab_hash": this_lab.hash,
                                       "lab_name": this_lab.name,
                                       "exceeded_limit": new_hist.exceeded_limit,
                                       "maximum_people": this_lab.max_number_of_people,
                                       "check_in": new_hist.checkin.astimezone(tz).strftime("%A, %d %b %Y, %H:%M"),
                                       "check_out": new_hist.checkout.astimezone(tz).strftime("%A, %d %b %Y, %H:%M"),
                                       "show_ask_feedback": True})
                return render(request, 'Page/lab_checkin_successful_new.html',
                              {"lab_hash": this_lab.hash,
                               "lab_name": this_lab.name,
                               "exceeded_limit": new_hist.exceeded_limit,
                               "maximum_people": this_lab.max_number_of_people,
                               "check_in": new_hist.checkin.astimezone(tz).strftime("%A, %d %b %Y, %H:%M"),
                               "check_out": new_hist.checkout.astimezone(tz).strftime("%A, %d %b %Y, %H:%M")})
        else:
            error_message = "เซสชั่นหมดอายุ กรุณาสแกน QR Code ใหม่อีกครั้ง"
            return render(request, 'Page/error.html', {"error_message": error_message, "this_lab": this_lab})
    else:
        error_message = "เซสชั่นหมดอายุ กรุณาสแกน QR Code ใหม่อีกครั้ง"
        return render(request, 'Page/error.html', {"error_message": error_message, "this_lab": this_lab})


def check_out(request, lab_hash):  # api
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))
    person = Person.objects.get(user=request.user)
    out_local_time = datetime.datetime.now(tz)
    log = History.objects.filter(person=person, lab__hash=lab_hash).order_by('checkin').last()
    log.checkout = out_local_time
    log.save()
    if request.GET.get('next_lab'):
        return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(request.GET['next_lab'],)))
    return render(request, 'Page/check_out_success.html', {"lab_name": log.lab.name})


def add_feedback_api(request):
    rating = request.POST.get("rating", "0")
    comment = request.POST.get("comment", "")
    print("recieve rating : " + rating + " star")
    print("comment : " + comment)
    
    rating = int(rating) if rating.isnumeric() else 0
    new_feedback = Feedback.objects.create(star=rating, text=comment)
    new_feedback.save()

    return HttpResponse(status=200)


def staff_signup(request):
    username_flag = False
    email_flag = False
    password_flag = False
    lab_flag = False
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if User.objects.filter(username=request.POST['username']):
            username_flag = True
        if User.objects.filter(email=request.POST['email']):
            email_flag = True
        if request.POST['password1'] != request.POST['password2']:
            password_flag = True
        if Lab.objects.filter(name=request.POST['lab_name']):
            lab_flag = True
        if LabPending.objects.filter(name=request.POST['lab_name']):
            lab_flag = True
        if (username_flag or email_flag or password_flag or lab_flag) is True:
            return render(request, 'Page/homepage.html', {'username_flag': username_flag, 'email_flag': email_flag,
                                                          'password_flag': password_flag, 'lab_flag': lab_flag})
        if form.is_valid():
            if request.POST['role'] == 'staff':
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                LabPending.objects.create(staff_user=user, name=request.POST['lab_name'], max=request.POST['max_lab'],
                                          lab_head_first_name=request.POST['lab_head_first_name'],
                                          lab_head_last_name=request.POST['lab_head_last_name'],
                                          head_email=request.POST['head_email'])
                current_site = get_current_site(request)
                mail_subject = request.POST['lab_name'] + ' Lab request'
                to_email = 'labrequest@cony.codes'
                message_admin = {to_email: {'user': user.username, 'domain': current_site.domain,
                                            'user_first_name': user.first_name, 'user_last_name': user.last_name,
                                            'user_email': user.email,
                                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                            'token': default_token_generator.make_token(user),
                                            'lab_name': request.POST['lab_name'],
                                            'lab_head_name': request.POST['lab_head_first_name'] + " " + request.POST[
                                                'lab_head_last_name'],
                                            'head_email': request.POST['head_email'],
                                            'max_lab': request.POST['max_lab']}}

                email = EmailMessage(mail_subject, to=[to_email])
                email.template_id = 'lab-request-admin'
                email.merge_data = message_admin
                email.send()

                message_requester = {form.cleaned_data.get('email'): {'username': user.username,
                                                                      'lab_name': request.POST['lab_name'],
                                                                      'max_lab': request.POST['max_lab'],
                                                                      'lab_head_name': request.POST[
                                                                                           'lab_head_first_name'] + " " +
                                                                                       request.POST[
                                                                                           'lab_head_last_name'],
                                                                      'head_email': request.POST['head_email']}}
                email = EmailMessage('เราได้รับคำขอใช้งาน Labtrack แล้ว', to=[form.cleaned_data.get('email')])
                email.template_id = 'lab-request-user'
                email.merge_data = message_requester
                email.send()
                return render(request, 'Page/homepage.html', {'correct_flag': True})
            if request.POST['role'] == 'lab_head':
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                LabPending.objects.create(staff_user=user, name=request.POST['lab_name'], max=request.POST['max_lab'])
                current_site = get_current_site(request)
                mail_subject = request.POST['lab_name'] + ' Lab request'
                to_email = 'labrequest@cony.codes'
                message_admin = {to_email: {'user': user.username, 'domain': current_site.domain,
                                            'user_first_name': user.first_name, 'user_last_name': user.last_name,
                                            'user_email': user.email,
                                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                            'token': default_token_generator.make_token(user),
                                            'lab_name': request.POST['lab_name'],
                                            'max_lab': request.POST['max_lab']}}

                email = EmailMessage(mail_subject, to=[to_email])
                email.template_id = 'lab-request-admin'
                email.merge_data = message_admin
                email.send()

                message_requester = {form.cleaned_data.get('email'): {'username': user.username,
                                                                      'lab_name': request.POST['lab_name'],
                                                                      'max_lab': request.POST['max_lab'],
                                                                      'lab_head_name': '-',
                                                                      'head_email': '-'}}
                email = EmailMessage('เราได้รับคำขอใช้งาน Labtrack แล้ว', to=[form.cleaned_data.get('email')])
                email.template_id = 'lab-request-user'
                email.merge_data = message_requester
                email.send()
                return render(request, 'Page/homepage.html', {'correct_flag': True})
        else:
            return render(request, 'Page/homepage.html', {'error_flag': True})
    else:
        return HttpResponseRedirect('/')


def questionnaire_views(request):  # api for logging out
    return render(request, 'Page/questionnaire.html')


def scrollanime(request):  # api for logging out
    return render(request, 'Page/scrollanimation.html')
