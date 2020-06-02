from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Lab(models.Model):
    name = models.CharField(max_length=300,null=True)
    amount = models.IntegerField(blank=True)
    def __str__(self):
        return self.name
class Person(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=13, blank=True)
    check_in_status = models.BooleanField(blank=True,default=False)
    name= models.CharField(max_length=60, blank=True)
    tel = models.CharField(max_length=10, blank=True)
    def __str__(self):
        return self.student_id
    def check_in(self):
        self.check_in_status = True
        self.save()
    def check_out(self):
        self.check_in_status = False
        self.save()
class History(models.Model):
#   id_by_date = models.อะไรสักอย่าง
    person = models.ForeignKey(Person,on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    checkin = models.DateTimeField(null=True,auto_now_add=True)
    checkout = models.DateTimeField(null=True)
    def __str__(self):
        return self.lab.name


