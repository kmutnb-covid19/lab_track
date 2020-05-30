# pipeline is custom function use when user logged in with facebook

import re
from django.contrib.auth.models import User
from kmutnbtrackapp.models import StudentID


# create user UserInfo object
def get_student_id(backend, user, response, *args, **kwargs):
    if response.get('email').startswith('s') and int(response.get('email')[1]).isdigit():
        student_id = re.findall(r'\d+', response.get('email'))
        print(student_id[0])
        username = (response.get('email')).split("@")[0]
        user = User.objects.get(username=username)
        StudentID.objects.create(user=user, student_id=student_id[0])
