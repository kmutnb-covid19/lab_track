from django.db import models
from django.contrib.auth.models import User
import datetime


# Create your models here.
class Lab(models.Model):
    name = models.CharField(max_length=300, null=True)
    amount = models.IntegerField(blank=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    email = models.EmailField(blank=True, null=True)
    student_id = models.CharField(max_length=13, blank=True)
    check_in_status = models.BooleanField(blank=True, default=False)
    is_student = models.BooleanField(blank=True, default=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def check_in(self):
        self.check_in_status = True
        self.save()

    def check_out(self):
        self.check_in_status = False
        self.save()


class History(models.Model):
    #   id_by_date = models.อะไรสักอย่าง
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    checkin = models.DateTimeField(null=True, auto_now_add=True)
    checkout = models.DateTimeField(null=True)

    def __str__(self):
        return self.lab.name
