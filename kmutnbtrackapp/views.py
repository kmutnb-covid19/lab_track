"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""
from datetime import datetime, timedelta
import csv

from django.core.exceptions import ValidationError
from django.db.models import F
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from kmutnbtrackapp.models import *
from kmutnbtrackapp.forms import SignUpForm


# Create your views here.

def home(request):
    if request.GET:
        lab_hash = request.GET.get('next')
        if not request.user.is_authenticated:  # check if user do not login
            return HttpResponseRedirect(reverse("kmutnbtrackapp:login", args=(lab_hash,)))
        return HttpResponseRedirect(reverse("kmutnbtrackapp:lab_home", args=(lab_hash,)))
    return HttpResponse('Waiting for beautiful homepage....')


def lab_home_page(request, lab_hash):  # this function is used when user get in home page
    if not request.user.is_authenticated:  # if user hasn't login
        lab_name = Lab.objects.get(hash=lab_hash).name
        return render(request, 'Page/lab_home.html', {"lab_name": lab_name, "lab_hash": lab_hash})
        # render page for logging in in that lab

    else:  # if user already login and not check in yet
        time_option = compare_current_time()
        lab_object = Lab.objects.get(hash=lab_hash)
        lab_name = lab_object.name
        now_datetime = datetime.datetime.now()
        midnight_time = now_datetime.replace(hour=23, minute=59, second=59, microsecond=0)
        current_people = History.objects.filter(lab=lab_object, checkout__gte=now_datetime,
                                                checkout__lte=midnight_time).count()
        return render(request, 'Page/lab_checkin.html', {"lab_name": lab_name,
                                                         "lab_hash": lab_hash,
                                                         "time_option": time_option,
                                                         "time_now_hour": datetime.datetime.now().hour,
                                                         "time_now_minute": datetime.datetime.now().minute,
                                                         "current_people": current_people
                                                         })  # render page for checkin


def signup(request):  # when stranger click 'Signup and Checkin'
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
            return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_name,)))
    # didn't receive POST
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_api(request):  # api when stranger login
    pass


def logout_api(request):  # api for logging out
    logout(request)
    lab_hash = request.GET.get("lab", '')
    return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))


def compare_current_time():  # make check out valid
    now_datetime = datetime.datetime.now()
    noon = now_datetime.replace(hour=12, minute=0, second=0, microsecond=0)  # noon time value
    four_pm = now_datetime.replace(hour=16, minute=0, second=0, microsecond=0)  # evening time value
    eight_pm = now_datetime.replace(hour=20, minute=0, second=0, microsecond=0)  # night time value
    if now_datetime < noon:  # return for use in templates
        return 1
    elif noon < now_datetime < four_pm:
        return 2
    elif noon < now_datetime < eight_pm and now_datetime > four_pm:
        return 3
    else:
        return 4


def check_in(request, lab_hash):  # when user checkin record in history
    person = Person.objects.get(user=request.user)
    lab_obj = Lab.objects.get(hash=lab_hash)
    time_checkout = request.POST.get('check_out_time')  # get check out time
    now_datetime = datetime.datetime.now()
    lab_name = Lab.objects.get(hash=lab_hash).name
    datetime_checkout = now_datetime.replace(hour=int(time_checkout.split(":")[0]),
                                             minute=int(
                                                 time_checkout.split(":")[1]))  # get check out time in object datetime
    if datetime_checkout < now_datetime:
        return HttpResponse('''<script>alert("ไม่สามารถเลือกเวลาในอดีตได้!");history.go(-1);</script>''')
    if Lab.objects.filter(hash=lab_hash).exists():  # check that lab does exists
        log = History.objects.create(person=person, lab=lab_obj, checkin=datetime.datetime.now(),
                                     checkout=datetime_checkout)
        return render(request, 'home.html',
                      {"lab_hash": lab_hash, "already_checkin": 1, "lab_name": lab_name,
                       "check_in": (log.checkin + timedelta(hours=7)).strftime("%A, %d %B %Y, %I:%M %p"),
                       "check_out": log.checkout.strftime("%A, %d %B %Y, %I:%M %p")})
    else:  # lab does not exists
        error_message = "QR code ไม่ถูกต้อง"
        return render(request, 'home.html', {"error_message": error_message})


def query_search(mode, keyword, start, stop):
    histories = History.objects.all()
    if not isinstance(start, type(datetime.datetime.now())):
        print(start)
        try:
            start = datetime.datetime.strptime(start,
                                            "%Y-%m-%dT%H:%M")  # convert from "2020-06-05T03:29" to Datetime object
        except:
            start = datetime.datetime.fromtimestamp(0)

    if not isinstance(stop, type(datetime.datetime.now())):
        try:
            stop = datetime.datetime.strptime(stop,
                                            "%Y-%m-%dT%H:%M")  # convert from "2020-06-05T03:29" to Datetime object
        except:
            stop = datetime.datetime.now()
     
    histories = histories.exclude(Q(checkin__gt=stop) | Q(checkout__lt=start))

    if keyword != "":  # if have specific keyword
        if mode == "id":
            histories = histories.filter(Q(person__student_id__startswith=keyword))
        elif mode == "name":
            histories = histories.filter(
                Q(person__first_name__startswith=keyword) | Q(person__last_name__startswith=keyword))
        elif mode == "lab":
            histories = histories.filter(Q(lab__name__startswith=keyword))
        elif mode == "tel":
            histories = histories.filter(Q(person__tel__startswith=keyword))
    
    return histories

    


def history_search(request):
    if request.user.is_superuser:
        keyword = request.GET.get('keyword', '')
        start = request.GET.get('from', '')
        stop = request.GET.get('to', '')
        mode = ""
        histories = History.objects.all()
        if request.GET:  # if request has parameter
            mode = request.GET.get('mode', '')
            histories = query_search(mode, keyword, start, stop)
        # p = Paginator(histories, 24)
        # page_range = p.page_range
        # shown_history = p.page(page)
        return render(request, 'admin/history_search.html',
                    {'shown_history': histories,
                    'keyword': keyword,
                    'select_mode': mode,
                    'start': start,
                    'stop':stop
                    # 'page_number': page,
                    # 'page_range': page_range,
                    })
    else:
        return HttpResponse("Permission Denined")


def export_normal_csv(request):
    if request.user.is_superuser:
        mode = request.GET.get('mode', '')
        keyword = request.GET.get('keyword', '')
        start = request.GET.get('from', '')
        stop = request.GET.get('to', '')
        histories = query_search(mode, keyword, start, stop)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Person Name', 'Lab Name', 'Check in time', 'Check out time'])
        for user in histories:
            writer.writerow([str(user.person.student_id),
                            user.person,
                            user.lab,
                            user.checkin + timedelta(hours=7),
                            user.checkout + timedelta(hours=7)])
        response['Content-Disposition'] = 'attachment; filename="user_data.csv"'
        return response
    else:
        return HttpResponse("Permission Denined")


def filter_risk_user(mode, keyword):
    risk_people_data = []
    risk_people_notify = []
    target_historys = query_search(mode, keyword, 0, 0) # get all historys with only the infected person
    if target_historys != 'EMPTY':
        for user in target_historys: # for each row of infected person
            session_historys = query_search('lab', user.lab, user.checkin, user.checkout) # 
            for session in session_historys:
                risk_people_data.append((session.person.student_id,
                                        session.person.first_name + ' ' + session.person.last_name,
                                        '',
                                        session.lab,
                                        session.checkin,
                                        session.checkout,
                                        ))
                risk_people_notify.append([session.person.student_id,
                                        session.person.first_name + ' ' + session.person.last_name,
                                        session.person.email,
                                        session.lab,
                                        ])

    return list(set(risk_people_data)), risk_people_notify



def risk_people_search(request):
    if request.user.is_superuser:
        risk_people_data = "EMPTY"
        keyword = ""
        mode = ""
        if request.GET:  # if request has parameter
            mode = request.GET.get('mode', '')
            keyword = request.GET.get('keyword', '')
            risk_people_data, risk_people_notify = filter_risk_user(mode, keyword)

        return render(request, 'admin/risk_people_search.html',
                        {'shown_history': risk_people_data,
                        'keyword': keyword,'select_mode' : mode,
                        })
    else:
        return HttpResponse("Permission Denined")


def notify_user(request):
    if request.user.is_superuser:
        mode = request.GET.get('mode', '')
        keyword = request.GET.get('keyword', '')
        risk_people_data, risk_people_notify = filter_risk_user(mode, keyword)
        #remove duplicate user'info
        user_info =[]
        for each_list in risk_people_notify:
            std_id = each_list[0]
            name = each_list[1]
            email = each_list[2]
            temp_list = [std_id,name,email]
            for each in risk_people_notify:
                if each[1] == name and each[3] not in temp_list :
                    temp_list.append(each[3])
            user_info.append(tuple(temp_list))
        risk_people_notify = set(user_info)

        for each_user in risk_people_notify:
            student_id = each_user[0]
            first_last_name = each_user[1]
            user_email = each_user[2]
            lab_name = []
            for each_lab in each_user[3:]:
                lab_name.append(each_lab)

            subject = 'เทสการแจ้งเตือน'
            message = render_to_string('admin/email.html', {'student_id': student_id,
                                                            'user_email': user_email,
                                                            'first_last_name': first_last_name,
                                                            'lab_name': lab_name,
                                                            })
            email = EmailMessage(subject, message, to=[user_email])
            email.send()

            return render(request,'admin/notify.html',
                                {'notify_status': True,
                                })
    else:
        return HttpResponse("Permission Denined")

def export_risk_csv(request):
    if request.user.is_superuser:
        mode = request.GET.get('mode', '')
        keyword = request.GET.get('keyword', '')
        risk_people_data, not_use = filter_risk_user(mode, keyword)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Person Name', 'Phone number', 'Lab Name', 'Check in time', 'Check out time'])
        for user in risk_people_data:
            user = list(user)
            user[4] = user[4] + timedelta(hours=7)
            user[5] = user[5] + timedelta(hours=7)
            writer.writerow(user)
        response['Content-Disposition'] = 'attachment; filename="risk_user_data.csv"'
        return response
    else:
        return HttpResponse("Permission Denined")


def generate_qr_code(request):
    if request.user.is_superuser:
        site_url = get_current_site(request)
        selected_lab = ""
        selected_lab_name = ""
        selected_lab_hash = ""
        all_lab_name = Lab.objects.all().order_by("name").values_list('name', flat=True)
        all_lab_hash = Lab.objects.all().order_by("name").values_list('hash', flat=True)
        if request.POST.get("lab_selector"):
            selected_lab = request.POST["lab_selector"]
            selected_lab_name = all_lab_name[int(selected_lab)]
            selected_lab_hash = all_lab_hash[int(selected_lab)]
        return render(request, 'admin/qr_code_generate.html', {"all_lab_name": all_lab_name,
                                                            "selected_lab_hash": selected_lab_hash,
                                                            "selected_lab_name": selected_lab_name,
                                                            "selected_lab": selected_lab, 'domain': site_url.domain})
    else:
        return HttpResponse("Permission Denined")
