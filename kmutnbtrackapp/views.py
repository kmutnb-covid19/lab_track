"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""
import datetime
import csv

from django.db.models import F
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import logout, authenticate, login
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

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

        return render(request, 'home.html', {"room_name": lab_name, 'room_amount': amount})
    else:
        error_message = "กรุณาสเเกน QR code หน้าห้อง หรือติดต่ออาจารย์ผู้สอน"
        return render(request, 'home.html', {"error_message": error_message})


def check_in(request, lab_name):  # api
    person = Person.objects.get(user=request.user)
    lab_obj = Lab.objects.get(name=lab_name)
    if Person.objects.get(user=request.user).check_in_status:  # user try to check in but he forget to check out
        lab_name = History.objects.get(person=person, checkout=None).lab.name
        return render(request, 'home.html',
                      {"check_in_status": Person.objects.get(user=request.user).check_in_status,
                       "room_check_in": lab_name})
    elif Lab.objects.filter(name=lab_name).exists():  # check that lab does exists
        if History.objects.filter(person=person,lab=lab_obj).count() != 0:  # เช็คอินครั้งแรก
            time = History.objects.filter(person=person, lab=lab_obj).order_by('checkin').last() # เอาตัวสุดท้ายที่อยู่ในโมเดลของประวัติโดยเรียงตามเวลาจะได้เวลาล่าสุดที่ check in lab นี้
            if datetime.datetime.now().hour - time.checkin.hour >= 1 or datetime.datetime.now().day > time.checkin.day:
                person.check_in()
                Log = History.objects.create(person=person, lab=lab_obj)
                Log.checkin = datetime.datetime.now()
                Log.save()
                return render(request, 'home.html', {"room_check_in": lab_name, "localtime": Log.checkin})
            else:
                already_checkin = 1
                return render(request, 'home.html', {"room_check_in": lab_name, "already_checkin": already_checkin})
        else:
            person.check_in()
            Log = History.objects.create(person=person, lab=lab_obj)
            return render(request, 'home.html',
                          {"room_check_in": lab_name, "localtime": Log.checkin})
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

def querry_search(mode, keyword, start, stop):
    histories = History.objects.all()

    if type(start) != type(datetime.datetime.now()):
        try:
            start = datetime.datetime.strptime(start,
                                               "%Y-%m-%dT%H:%M")  # convert from "2020-06-05T03:29" to Datetime object
        except:
            start = datetime.datetime.fromtimestamp(0)

    if type(stop) != type(datetime.datetime.now()):
        try:
            stop = datetime.datetime.strptime(stop, "%Y-%m-%dT%H:%M")  # convert from "2020-06-05T03:29" to Datetime object
        except:
            stop = datetime.datetime.now()
    histories = histories.exclude(Q(checkin__gt=stop) | Q(checkout__lt=start))
    if keyword != "":  # if have specific keyword
        if mode == "id":
            histories = histories.filter(Q(person__student_id__startswith=keyword))
        elif mode == "name":
            histories = histories.filter(Q(person__first_name__startswith=keyword) | Q(person__last_name__startswith=keyword))
        elif mode == "lab":
            histories = histories.filter(Q(lab__name__contains=keyword))
        elif mode == "tel":
            histories = histories.filter(Q(person__tel__contains=keyword))
        histories = histories.exclude(Q(checkin__gt=stop) | Q(checkout__lt=start))
        return histories
    else:
        return histories


def history_search(request,page=1):
    if request.user.is_superuser:
        if request.GET: # if request has parameter
            mode = request.GET.get('mode','')
            keyword = request.GET.get('keyword','')
            start = request.GET.get('from','')
            stop = request.GET.get('to','')

            histories = querry_search(mode, keyword, start, stop)

        #p = Paginator(histories, 24)
        #page_range = p.page_range
        #shown_history = p.page(page)
            return render(request, 'admin/history_search.html',
                    {'shown_history': histories,
                        #'page_number': page,
                        #'page_range': page_range,
                    })
        else:
            return render(request, 'admin/history_search.html',
                    {'shown_history': '',
                        #'page_number': page,
                        #'page_range': page_range,
                    })

def export_normal_csv(request):
    mode = request.GET.get('mode', '')
    keyword = request.GET.get('keyword', '')
    start = request.GET.get('from', '')
    stop = request.GET.get('to', '')
    histories = querry_search(mode, keyword, start, stop)
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Person Name', 'Lab Name', 'Check in time', 'Check out time'])

    for user in histories:
        writer.writerow([str(user.person.student_id), user.person, user.lab, user.checkin, user.checkout])

    response['Content-Disposition'] = 'attachment; filename="user_data.csv"'
    return response

def filter_risk_user(mode, keyword):
    start = 0
    stop = 0
    risk_people_data = []
    risk_people_notify = []
    target_history = querry_search(mode, keyword, start, stop)

    if target_history != 'EMPTY':
        for user in target_history:
            lab = user.lab
            checkin = user.checkin
            checkout = user.checkout
            print(user.person, user.lab, user.checkin, user.checkout)
            session_history = querry_search('lab', lab, user.checkin, user.checkout)
            for session in session_history:
                print('            ', session.person, session.lab, session.checkin, session.checkout)
                risk_people_data.append([str(session.person.student_id),
                                         session.person.first_name + ' ' + session.person.last_name,
                                         '',
                                         session.lab,
                                         session.checkin,
                                         session.checkout,
                                         ])
                risk_people_notify.append([str(session.person.student_id),
                                         session.person.first_name + ' ' + session.person.last_name,
                                         session.lab,
                                         session.person.email,
                                         ])
                    #index=> (0,stuid)(1,first last)(3,lab)(4,checkin)(5,checkout)(6,email)
                    #data -> tel, no email
                    #notify -> no tel, email, no checkin-out
    return risk_people_data, risk_people_notify

def risk_people_search(request):
    if request.user.is_superuser:
        if request.GET: # if request has parameter
            mode = request.GET.get('mode','')
            keyword = request.GET.get('keyword','')

            risk_people_data,risk_people_notify = filter_risk_user(mode, keyword)
            print(risk_people_data)

            return render(request, 'admin/risk_people_search.html',
                    {'shown_history': risk_people_data,
                     'keyword': keyword,
                    })
        else:
            return render(request, 'admin/risk_people_search.html',
                    {'shown_history': '',
                    })

def notify_user(request):
    mode = request.GET.get('mode', '')
    keyword = request.GET.get('keyword', '')

    risk_people_data, risk_people_notify = filter_risk_user(mode, keyword)
    for each_user in risk_people_notify:
        student_id = each_user[0]
        first_last_name = each_user[1]
        lab_name = each_user[2]
        user_email = each_user[3]

        subject = 'เทสการแจ้งเตือน'
        message = render_to_string('admin/email.html',{'student_id': student_id,
                                                'user_email': user_email,
                                                'first_last_name': first_last_name,
                                                'lab_name': lab_name,
                                                })
        email = EmailMessage(subject, message, to=[user_email])
        email.send()

    return render(request,'admin/notify.html',
                {'notify_status': True,
                })

def export_risk_csv(request):
    mode = request.GET.get('mode', '')
    keyword = request.GET.get('keyword', '')
    risk_people_data = filter_risk_user(mode, keyword)

    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Person Name', 'Lab Name', 'Check in time', 'Check out time'])

    for user in risk_people_data:
        writer.writerow(user)

    response['Content-Disposition'] = 'attachment; filename="risk_user_data.csv"'
    return response
