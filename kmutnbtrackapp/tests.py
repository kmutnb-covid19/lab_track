from datetime import datetime
from datetime import timedelta
import time
import json
import requests
import random
from random import randrange

import names # pip install names
from django.test import TestCase
from django.test import LiveServerTestCase
from django.test import Client
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from kmutnbtrackapp.models import History, Person, Lab, User
# Create your tests here.

class Searching_test(LiveServerTestCase):
    def random_datetime(self):
        """
        This function will return a random datetime between two datetime 
        objects.
        """
        start = datetime.strptime('1/1/2020 9:00', '%d/%m/%Y %H:%M')
        end = datetime.strptime('1/1/2020 16:00', '%d/%m/%Y %H:%M')
        delta = end - start
        int_delta = (delta.days * 24 * 60) + (delta.seconds / 60)
        random_minute = randrange(int_delta)
        return start + timedelta(minutes=random_minute)

    def setUp(self):
        labA = Lab.objects.create(name="computer", amount=10)
        labB = Lab.objects.create(name="ece", amount=10)
        labC = Lab.objects.create(name="physic", amount=10)
        lablist = [labA, labB, labC]
        for i in range(50):
            firstname = names.get_first_name() + str(randrange(100))
            lastname = names.get_last_name()
            u = User.objects.create(username=firstname,email='',password=lastname)
            p = Person.objects.create(user=u, first_name=firstname, last_name=lastname)
            checkin_time = self.random_datetime()
            checkout_time = checkin_time + timedelta(hours=random.choice([1,2,3]))
            a = History.objects.create( person=p, lab=random.choice(lablist), checkin=checkin_time, checkout=checkout_time)
            a.checkin=checkin_time
            a.save()

    def test_can_query_by_name(self):
        pass
    def test_can_query_by_lab_name(self):
        pass
    def test_can_query_by_time_period(self): 
        start = datetime.strptime("2020-1-2T9:00", "%Y-%m-%dT%H:%M")
        stop = datetime.strptime("2020-1-2T14:00", "%Y-%m-%dT%H:%M")
        histories = History.objects.all()
        histories = histories.exclude( Q(checkin__gt=stop) | Q(checkout__lt=start) )
        for h in histories:
            self.assertTrue(
                (h.checkin >= start and h.checkin <= end) # intersect forward
                or (h.checkout >= start and h.checkout <= end) # intersect backward
                or (h.checkin >= start and h.checkout <= end)  # intersect inside
            )
    def test_can_search_people_who_close_to_infected_person(self):
        pass
