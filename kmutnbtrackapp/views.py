"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""

from datetime import datetime, timedelta

import csv
import qrcode
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import re

from django.db.models import Q
from django.shortcuts import render
from django.core import management
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.contrib.auth import logout, authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, INTERNAL_RESET_SESSION_TOKEN, \
    PasswordResetCompleteView

from kmutnbtrackapp.models import *
from kmutnbtrackapp.dashboard import *


# Create your views here.

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'

    def post(self, request, *args, **kwargs):
        self.extra_email_context = {
            'lab_hash': self.request.POST['lab_hash']
        }
        return super().post(request, *args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])
        lab_hash = self.request.GET.get('next')
        self.success_url = reverse_lazy('password_reset_complete', kwargs={'next': lab_hash})

        if self.user is not None:
            print(lab_hash)
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token) + "?next=" + lab_hash
                    return HttpResponseRedirect(redirect_url)
        return self.render_to_response(self.get_context_data())


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        assert 'next' in kwargs
        self.extra_context = {
            'lab_hash_receive': kwargs['next'],
            'lab_name': Lab.objects.get(hash=kwargs['next']).name
        }
        return super().get_context_data(**kwargs)


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
        now_datetime = datetime.datetime.now()

        if History.objects.filter(person=person, checkin__lte=now_datetime,
                                  checkout__gte=now_datetime).exists():  # if have lastest history which checkout not at time
            last_lab_hist = History.objects.filter(person=person, checkin__lte=now_datetime, checkout__gte=now_datetime)
            last_lab_hist = last_lab_hist[0]

            if last_lab_hist.lab.hash == lab_hash:  # if latest lab is same as the going lab
                return render(request, 'Page/check_out_before_due_new.html', {"last_lab": last_lab_hist.lab})

            else:  # if be another lab
                return render(request, 'Page/lab_checkout.html', {"last_lab": last_lab_hist.lab,
                                                                  "new_lab": this_lab})


        else:
            time_option = compare_current_time()
            lab_object = Lab.objects.get(hash=lab_hash)
            lab_name = lab_object.name
            now_datetime = datetime.datetime.now()
            midnight_time = now_datetime.replace(hour=23, minute=59, second=59, microsecond=0)
            current_people = History.objects.filter(lab=lab_object, checkout__gte=now_datetime,
                                                    checkout__lte=midnight_time).count()
            return render(request, 'Page/lab_checkin_new.html', {"lab_name": lab_name,
                                                                 "lab_hash": lab_hash,
                                                                 "time_option": time_option,
                                                                 "time_now_hour": datetime.datetime.now().hour,
                                                                 "time_now_minute": datetime.datetime.now().minute,
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
        return render(request, 'Page/signup_form.html', {'lab_hash': lab_hash})
    # Receive data from POST
    if request.method == "POST":
        lab_hash = request.POST.get('next', '')
        username = request.POST["username"]
        email = request.POST['email']
        password = request.POST['password']
        firstname = request.POST.get('first_name', '')
        lastname = request.POST.get('last_name', '')
        # Form is valid
        if User.objects.filter(username=username).count() == 0:  # if username is available
            # create new User object and save it
            u = User.objects.create(username=username, email=email)
            u.set_password(password)  # bypassing Django password format check
            u.save()
            # create new Person object
            Person.objects.create(user=u, first_name=firstname, last_name=lastname, email=email, is_student=False)
            # then login
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')

            return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))
        else:
            return JsonResponse({"status": "fail"})


def login_api(request):  # api when stranger login
    print("Here")
    if request.method == "GET":
        lab_hash = request.GET.get('next', '')
        print(lab_hash)
        if lab_hash != '':
            lab_name = Lab.objects.get(hash=lab_hash).name
        return render(request, 'Page/log_in.html', {'lab_hash': lab_hash, 'lab_name': lab_name})

    if request.method == "POST":
        lab_hash = request.POST.get('next', '')
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # auth username and password
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))
        else:
            return JsonResponse({"status": "fail"})
    # didn't receive POST


def logout_api(request):  # api for logging out
    logout(request)
    try:
        lab_hash = request.GET.get("lab")
        return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(lab_hash,)))
    except:
        return HttpResponseRedirect("/")


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
    this_lab = Lab.objects.get(hash=lab_hash)

    checkout_time_str = request.POST.get('check_out_time')  # get check out time
    now_datetime = datetime.datetime.now()

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
                           "check_in": (new_hist.checkin + timedelta(hours=7)).strftime("%A, %d %B %Y, %H:%M"),
                           "check_out": new_hist.checkout.strftime("%A, %d %B %Y, %H:%M")})


def check_out(request, lab_hash):  # api
    person = Person.objects.get(user=request.user)
    out_local_time = datetime.datetime.now()
    log = History.objects.filter(person=person, lab__hash=lab_hash).order_by('checkin').last()
    log.checkout = out_local_time
    log.save()
    if request.GET.get('next_lab'):
        return HttpResponseRedirect(reverse('kmutnbtrackapp:lab_home', args=(request.GET['next_lab'],)))
    return render(request, 'Page/check_out_success.html', {"lab_name": log.lab.name})


def query_search(mode, keyword, start, stop, search_mode):
    """search data in DB by time and keyword and return query set"""
    histories = History.objects.all()
    if not isinstance(start, type(datetime.datetime.now())):
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
    if search_mode == "normal":
        histories = histories.exclude(Q(checkout__gt=stop) | Q(checkout__lt=start))
    elif search_mode == "risk" and keyword != "":
        histories = histories.exclude(Q(checkin__gt=stop) | Q(checkout__lt=start))
    else:
        histories = "EMPTY"

    if keyword != "":  # if have specific keyword
        if mode == "id":
            histories = histories.filter(Q(person__student_id__startswith=keyword))
        elif mode == "name":
            histories = histories.filter(
                Q(person__first_name__startswith=keyword) | Q(person__last_name__startswith=keyword))
        elif mode == "lab":
            histories = histories.filter(Q(lab__name__startswith=keyword))
        # elif mode == "tel":
        #    histories = histories.filter(Q(person__tel__startswith=keyword))

    return histories


def history_search(request, page=1):
    """Received from the client and searched for information from the server and then sent back to the client"""
    if request.user.is_superuser:
        keyword = request.GET.get('keyword', '')
        start = request.GET.get('from', '')
        stop = request.GET.get('to', '')
        mode = request.GET.get('mode', '')
        histories = query_search(mode, keyword, start, stop, "normal")

        p = Paginator(histories, 36)
        num_pages = p.num_pages
        shown_history = p.page(page)

        split_url = request.get_full_path().split("/")
        print(split_url)
        if page == 1:
            prev_url = None

            if num_pages != 1:
                split_url[-2] = "2"
                next_url = "/".join(split_url)
            else:
                next_url = None

        elif page == num_pages:
            split_url[-2] = str(num_pages - 1)
            prev_url = "/".join(split_url)

            next_url = None

        else:
            split_url[-2] = str(page - 1)
            prev_url = "/".join(split_url)

            split_url[-2] = str(page + 1)
            next_url = "/".join(split_url)

        return render(request, 'admin/history_search.html',
                      {'shown_history': shown_history,
                       'keyword': keyword,
                       'select_mode': mode,
                       'start': start,
                       'stop': stop,
                       'current_page_number': page,
                       'prev_url': prev_url,
                       'next_url': next_url,

                       })
    else:
        return HttpResponse("Permission Denied")


def export_normal_csv(request):
    """export file csv log to user"""
    if request.user.is_superuser:
        mode = request.GET.get('mode', '')
        keyword = request.GET.get('keyword', '')
        start = request.GET.get('from', '')
        stop = request.GET.get('to', '')
        histories = query_search(mode, keyword, start, stop, "normal")
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Person Name', 'Lab Name', 'Check in time', 'Check out time'])
        for user in histories:
            writer.writerow([str(user.person.student_id),
                             user.person,
                             user.lab,
                             user.checkin + timedelta(hours=7),
                             user.checkout + timedelta(hours=7)])
        response['Content-Disposition'] = 'attachment; filename="file_log.csv"'
        return response
    else:
        return HttpResponse("Permission Denied")


def filter_risk_user(mode, keyword):
    """filter user if there near by infected in time"""
    risk_people_data = []
    risk_people_notify = []
    target_historys = query_search(mode, keyword, 0, 0, "risk")  # get all history with only the infected person
    if target_historys != 'EMPTY':
        for user in target_historys:  # for each row of infected person
            session_historys = query_search('lab', user.lab, user.checkin, user.checkout, "risk")  #
            for session in session_historys:
                risk_people_data.append((session.person.student_id,
                                         session.person.first_name + ' ' + session.person.last_name,
                                         session.lab,
                                         session.checkin,
                                         session.checkout,
                                         ))
                risk_people_notify.append([session.person.student_id,
                                           session.person.first_name + session.person.last_name,
                                           session.person.email,
                                           session.lab,
                                           ])

    return list(set(risk_people_data)), risk_people_notify


def risk_people_search(request):
    """Received from the client filter data and sent back to client"""
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
                       'keyword': keyword, 'select_mode': mode,
                       })
    else:
        return HttpResponse("Permission Denined")


def export_risk_csv(request):
    """export file risk user csv log to user"""
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
        response['Content-Disposition'] = 'attachment; filename="Risk Log.csv"'
        return response
    else:
        return HttpResponse("Permission Denined")


def notify_confirm(request):
    if request.user.is_superuser:
        mode = request.GET.get('mode', '')
        keyword = request.GET.get('keyword', '')
        return render(request, 'admin/notify_confirm.html', {'mode': mode,
                                                             'keyword': keyword,
                                                             })
    else:
        return HttpResponse("Permission Denined")


def notify_user(request, mode, keyword):
    if request.user.is_superuser:
        confirm = request.POST.get('confirm', '')
        if request.method == "POST" and confirm == "ยืนยัน":
            risk_people_data, risk_people_notify = filter_risk_user(mode, keyword)
            # remove duplicate user'info
            user_info = []
            for each_list in risk_people_notify:
                std_id = each_list[0]
                name = each_list[1]
                email = each_list[2]
                temp_list = [std_id, name, email]
                for each in risk_people_notify:
                    if each[1] == name and each[3] not in temp_list:
                        temp_list.append(each[3])
                user_info.append(tuple(temp_list))
            risk_people_notify = set(user_info)

            user_data = {}
            user_email = []
            for each_user in risk_people_notify:
                student_id = each_user[0]
                first_last_name = each_user[1]
                each_user_email = each_user[2]
                user_email.append(each_user_email)
                lab_name = ''
                for each_lab in each_user[3:]:
                    lab_name += str(each_lab) + ', '
                lab_name = lab_name[:-2]
                user_data[each_user_email] = {'student_id': student_id,
                                              'first_last_name': first_last_name,
                                              'user_email': each_user_email,
                                              'lab_name': lab_name}
            subject = 'แจ้งเตือนกลุ่มผู้มีความเสี่ยงติดเชื้อ covid-19'
            email = EmailMessage(subject, to=user_email)
            email.template_id = 'notify-labtrack'
            email.merge_data = user_data
            email.send()

            return render(request, 'admin/notify_status.html',
                          {'notify_status': True,
                           })
    else:
        return HttpResponse("Permission Denined")


def generate_qr_code(request, lab_hash):
    if request.user.is_superuser:
        site_url = "get_current_site(request)"
        lab_name = Lab.objects.get(hash=lab_hash).name
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(f"https://labtrack.cony.codes/lab/{lab_hash}/")
        qr.make()

        img_qr = qr.make_image()

        img_frame = Image.open("kmutnbtrackapp/static/qrcode_src/qr_frame.jpg")

        pos = (57, 135)
        img_frame.paste(img_qr, pos)

        draw = ImageDraw.Draw(img_frame)

        font_size = 38
        font = ImageFont.truetype("kmutnbtrackapp/static/qrcode_src/Prompt-Medium.ttf", 38)
        ascent, descent = font.getmetrics()
        (width, baseline), (offset_x, offset_y) = font.font.getsize(lab_name)

        if len(lab_name) > 24:
            # split to 2 line and draw here
            pass

        elif len(lab_name) > 14:  # long name -> reduce font size
            while width >= 305:
                font_size -= 1
                font = ImageFont.truetype("font/Prompt-Medium.ttf", font_size)
                ascent, descent = font.getmetrics()
                (width, baseline), (offset_x, offset_y) = font.font.getsize(lab_name)

            draw.text((82, 75 - ascent), lab_name, (255, 255, 255), font=font)
        else:
            draw.text((82, 75 - ascent), lab_name, (255, 255, 255), font=font)

        img_frame.save(f'media/{lab_name}_qrcode.jpg', quality=100, subsampling=0)
        with open(f'media/{lab_name}_qrcode.jpg', "rb") as f:
            response = HttpResponse(f.read(), content_type="image/jpeg")
            response['Content-Disposition'] = 'inline; filename=' + f'media/{lab_name}_qrcode.jpg'
            return response
    else:
        return HttpResponse("Permission Denined")


def call_dashboard(request):
    """load metadata check update and format it before send data to dashboard"""
    if request.user.is_superuser:
        """load and manage metadata"""
        meta_data = get_data_metadata()
        dataset = query_search('', '', meta_data["latest time"], datetime.datetime.now(), "normal")
        for user in dataset:
            if str(user.lab) in meta_data['lab']:
                if (str(user.checkout.year) + "/" + str(user.checkout.month) + "/" + str(user.checkout.day)) in \
                        meta_data['lab'][str(user.lab)]:
                    meta_data['lab'][str(user.lab)][
                        str(user.checkout.year) + "/" + str(user.checkout.month) + "/" + str(user.checkout.day)] += 1
                else:
                    meta_data['lab'][str(user.lab)][
                        str(user.checkout.year) + "/" + str(user.checkout.month) + "/" + str(user.checkout.day)] = 1
            else:
                meta_data['lab'][str(user.lab)] = {}
                meta_data['lab'][str(user.lab)][
                    str(user.checkout.year) + "/" + str(user.checkout.month) + "/" + str(user.checkout.day)] = 1
        meta_data["latest time"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        write_metadata(meta_data)

        """prepare data before sent to template"""
        pie_data = prepare_pie_data(meta_data)
        liner_data = prepare_liner_data(meta_data)
        histrogram_data = prepare_single_liner_data(meta_data)
        return render(request, 'admin/dashboard.html', {
            'pie_data': json.dumps(pie_data),
            'liner_data': json.dumps(liner_data),
            'histrogram_dump': json.dumps(histrogram_data),
            "histrogram_data": histrogram_data,
        })
    else:
        return HttpResponse("Permission Denined")


def backup(request):
    """ manually back up database """

    # call command python manage.py dbbackup
    management.call_command('dbbackup')

    messages.info(request, 'Database has been backed up successfully!')
    return HttpResponseRedirect('/admin')
