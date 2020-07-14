
import datetime

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from kmutnbtrackapp.models import *

tz = timezone.get_default_timezone()


def compare_current_time():  # make check out valid
    now_datetime = datetime.datetime.now(tz)
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


def query_search(mode, keyword, start, stop, search_mode):
    """search data in DB by time and keyword and return query set"""
    histories = History.objects.all()
    if not isinstance(start, type(datetime.datetime.now(tz))):
        try:
            start = datetime.datetime.strptime(start,
                                               "%Y-%m-%dT%H:%M")  # convert from "2020-06-05T03:29" to Datetime object
        except:
            start = datetime.datetime.fromtimestamp(0)
    if not isinstance(stop, type(datetime.datetime.now(tz))):
        try:
            stop = datetime.datetime.strptime(stop,
                                              "%Y-%m-%dT%H:%M")  # convert from "2020-06-05T03:29" to Datetime object
        except:
            stop = datetime.datetime.now(tz)
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
            keyword = keyword.split(" ")
            if len(keyword) == 1:
                histories = histories.filter(
                    Q(person__first_name__startswith=keyword[0]) | Q(person__last_name__startswith=keyword[0]))
            elif len(keyword) == 2:
                histories = histories.filter(Q(person__first_name__startswith=keyword[0]))
                histories = histories.filter(Q(person__last_name__startswith=keyword[1]))
        elif mode == "lab":
            histories = histories.filter(Q(lab__name__startswith=keyword))
    return histories


def sort_lab_name_risk_search(each_user):
    return str(each_user[2])


def sort_name_risk_search(each_user):
    return str(each_user[1])


def filter_risk_user(mode, keyword):
    """filter user if there near by infected in time"""
    risk_people_data = []
    risk_people_notify = []
    target_historys = query_search(mode, keyword, 0, 0, "risk")  # get all history with only the infected person
    if target_historys != 'EMPTY':
        for user in target_historys:  # for each row of infected person
            session_historys = query_search('lab', user.lab, user.checkin, user.checkout, "risk")  #
            for session in session_historys:
                std_id = session.person.student_id
                tel = session.person.user.username
                risk_people_data.append((std_id if std_id != '' else "-",
                                         session.person.first_name + ' ' + session.person.last_name,
                                         tel if tel != '' and tel[0] == "0" else "-",
                                         session.lab,
                                         session.checkin,
                                         session.checkout,
                                         ))
                risk_people_notify.append([session.person.student_id,
                                           session.person.first_name + ' ' + session.person.last_name,
                                           session.person.email,
                                           session.lab,
                                           ])
        risk_people_data.sort(key=sort_name_risk_search)
        risk_people_data.sort(key=sort_lab_name_risk_search)

    return risk_people_data, risk_people_notify




def superuser_login_required(func):
    def wrapper(request, *args, **kw):
        if request.user.is_superuser:
            return func(request, *args, **kw)
        else:
            return render(request, 'Page/error.html', {"error_message": "Permission denied"})

    return wrapper


def supervisor_login_required(func):
    def wrapper(request, *args, **kw):
        if request.user.is_superuser or request.user.groups.filter(name='Supervisor').exists():
            return func(request, *args, **kw)
        else:
            return render(request, 'Page/error.html', {"error_message": "Permission denied"})

    return wrapper

