"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""

import csv

import qrcode
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from django.contrib import messages
from django.core import management
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from kmutnbtrackapp.dashboard import *
from kmutnbtrackapp.views.help import *
from kmutnbtrackapp.views.help import tz


@supervisor_login_required
def history_search(request, page=1):
    """Received from the client and searched for information from the server and then sent back to the client"""
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


@supervisor_login_required
def view_lab(request, lab_hash):
    this_lab = Lab.objects.get(hash=lab_hash)
    now_datetime = datetime.datetime.now(tz)
    midnight_time = now_datetime.replace(hour=23, minute=59, second=59, microsecond=0)
    current_people = History.objects.filter(lab=this_lab,
                                            checkout__gte=now_datetime,
                                            checkout__lte=midnight_time)
    if request.GET.get('confirm') == 'true':
        for person in current_people:
            out_local_time = datetime.datetime.now(tz)
            person.checkout = out_local_time
            person.save()
        return HttpResponseRedirect(reverse('admin:kmutnbtrackapp_lab_changelist'))
    return render(request, 'admin/clear_lab.html', {'this_lab': this_lab, 'shown_history': current_people})


@superuser_login_required
def export_normal_csv(request):
    """export file csv log to user"""
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
                         user.checkin.astimezone(tz),
                         user.checkout.astimezone(tz)])
    response['Content-Disposition'] = 'attachment; filename="file_log.csv"'
    return response


@superuser_login_required
def risk_people_search(request):
    """Received from the client filter data and sent back to client"""
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


@superuser_login_required
def export_risk_csv(request):
    """export file risk user csv log to user"""
    mode = request.GET.get('mode', '')
    keyword = request.GET.get('keyword', '')
    if keyword != "":
        risk_people_data, not_use = filter_risk_user(mode, keyword)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(
            ['Student ID', 'Person Name', 'Phone number', 'Lab Name', 'Check in time', 'Check out time'])
        for user in risk_people_data:
            user = list(user)
            user[4] = user[4].astimezone(tz)
            user[5] = user[5].astimezone(tz)
            writer.writerow(user)
        response['Content-Disposition'] = 'attachment; filename="Risk Log.csv"'
        return response
    else:
        return redirect(risk_people_search)


@superuser_login_required
def notify_confirm(request):
    mode = request.GET.get('mode', '')
    keyword = request.GET.get('keyword', '')
    if keyword != "":
        return render(request, 'admin/notify_confirm.html', {'mode': mode,
                                                             'keyword': keyword,
                                                             })
    else:
        return redirect(risk_people_search)


@superuser_login_required
def notify_user(request, mode, keyword):
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
        subject = 'แจ้งเตือนกลุ่มผู้มีความเสี่ยงติดเชื้อ COVID-19'
        email = EmailMessage(subject, to=user_email)
        email.template_id = 'notify-labtrack'
        email.merge_data = user_data
        email.send()

        return render(request, 'admin/notify_status.html',
                      {'notify_status': True,
                       })


@supervisor_login_required
def generate_qr_code(request, lab_hash):
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


@supervisor_login_required
def call_dashboard(request):
    """load metadata check update and format it before send data to dashboard"""

    """load and manage metadata"""
    meta_data = get_data_metadata()
    dataset = query_search('', '', meta_data["latest time"], datetime.datetime.now(tz), "normal")

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
    meta_data["latest time"] = datetime.datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S.%f')
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


@superuser_login_required
def backup(request):
    """ manually back up database """

    # call command python manage.py dbbackup
    management.call_command('dbbackup')

    messages.info(request, 'Database has been backed up successfully!')
    return HttpResponseRedirect('/admin')
