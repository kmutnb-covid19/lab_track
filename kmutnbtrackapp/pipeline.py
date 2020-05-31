# pipeline is custom function use when user logged in with facebook

import re

from django.contrib.auth.models import User

from kmutnbtrackapp.models import Person


# create user UserInfo object
def get_student_id(backend, user, response, *args, **kwargs):
    if response.get('email').startswith('s') and str(response.get('email')[1]).isdigit():
        student_id = re.findall(r'\d+', response.get('email'))
        if not Person.objects.filter(student_id=student_id[0]).exists():
            username = (response.get('email')).split("@")[0]
            user = User.objects.get(username=username)
            Person.objects.create(user=user, student_id=student_id[0])
