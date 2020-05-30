from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class StudentID(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=13, blank=True)

    def __str__(self):
        return self.student_id
