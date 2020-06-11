from django.db import models
from django.contrib.auth.models import User, AnonymousUser
import datetime


# Create your models here.
class Lab(models.Model):
    name = models.CharField(max_length=300)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Person(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default="", blank=True)
    last_name = models.CharField(max_length=50, default="", blank=True)
    email = models.EmailField(default="", blank=True)
    student_id = models.CharField(max_length=13, default="", blank=True)
    is_checkin = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def check_in(self):
        self.is_checkin = True
        self.save()

    def check_out(self):
        self.is_checkin = False
        self.save()


class History(models.Model):
    #   id_by_date = models.อะไรสักอย่าง
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    checkin = models.DateTimeField(null=True, auto_now_add=True)
    checkout = models.DateTimeField(null=True)

    def __str__(self):
        return self.lab.name
