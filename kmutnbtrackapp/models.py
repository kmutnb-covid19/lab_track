from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Lab(models.Model):
    name = models.CharField(max_length=300, null=True)
    amount = models.IntegerField(blank=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=13, blank=True)
    check_in_status = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name + " " + self.student_id


class History(models.Model):
    #   id_by_date = models.อะไรสักอย่าง
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    checkin = models.DateTimeField(null=True)
    checkout = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.checkin.date()) + " " + self.lab.name + " " + self.person.user.first_name
