import random

from django.contrib.auth.models import User
from django.db import models


# Create your models here.

def create_id():
    return random.getrandbits(32)


class Lab(models.Model):
    name = models.CharField(max_length=60, blank=True, null=True)
    max_number_of_people = models.IntegerField(blank=True, default=20)
    hash = models.CharField(max_length=16, primary_key=True, default=create_id)

    def __str__(self):
        return self.name


class Person(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default="", blank=True)
    last_name = models.CharField(max_length=50, default="", blank=True)
    email = models.EmailField(default="", blank=True)
    student_id = models.CharField(max_length=13, default="", blank=True)
    is_student = models.BooleanField(default=False)
    ask_feedback = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name + " " + self.last_name


class History(models.Model):
    #   id_by_date = models.อะไรสักอย่าง
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    checkin = models.DateTimeField(null=True, auto_now_add=True)
    checkout = models.DateTimeField(null=True)
    exceeded_limit = models.BooleanField(default=False)

    def __str__(self):
        return self.lab.name


class LabPending(models.Model):
    staff_user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=60, blank=True, null=True)
    max = models.IntegerField(blank=True, default=20)
    lab_head_first_name = models.CharField(max_length=60, blank=True, null=True)
    lab_head_last_name = models.CharField(max_length=60, blank=True, null=True)
    head_email = models.CharField(max_length=60, blank=True, null=True)

    def __str__(self):
        return self.name

class Feedback(models.Model):
    star = models.IntegerField(default=0)
    text = models.TextField(default="")