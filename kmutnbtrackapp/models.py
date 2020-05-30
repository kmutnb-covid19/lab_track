from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Lab(models.Model):
    lab_name = models.CharField(max_length=300, null=True)
    amount_people = models.IntegerField(blank=True)

    def __str__(self):
        return self.lab_name


class StudentID(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=13, blank=True)

    def __str__(self):
        return self.student_id


class History(models.Model):
    #   id_by_date = models.อะไรสักอย่าง
    Student = models.ForeignKey(StudentID, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    lab_name = models.CharField(max_length=300, null=True)
    checkin = models.DateTimeField(null=True)
    checkout = models.DateTimeField(null=True)
    student_name = models.CharField(max_length=50, blank=True)
    student_ids = models.CharField(max_length=13, blank=True)

    def __str__(self):
        return str(self.checkin.date()) + " " + self.lab_name + " " + self.student_name
