"""
Imports should be grouped in the following order:

1.Standard library imports.
2.Related third party imports.
3.Local application/library specific imports.
"""

import os
import csv
import qrcode

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import datetime, timedelta


from django.db.models import Q
from django.shortcuts import render, redirect
from django.core import management
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, INTERNAL_RESET_SESSION_TOKEN
from django.contrib.auth.views import PasswordResetCompleteView
from django.utils import timezone

from kmutnbtrackapp.models import *
from kmutnbtrackapp.dashboard import *


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
        return HttpResponse("Permission Denied")


def call_dashboard(request):
    """load metadata check update and format it before send data to dashboard"""
    if request.user.is_superuser:
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
    else:
        return HttpResponse("Permission Denied")


def backup(request):
    """ manually back up database """

    # call command python manage.py dbbackup
    management.call_command('dbbackup')

    messages.info(request, 'Database has been backed up successfully!')
    return HttpResponseRedirect('/admin')
