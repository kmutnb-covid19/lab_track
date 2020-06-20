from datetime import datetime
from datetime import timedelta
import time
import json
import requests
import random
from random import randrange
import pytz

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


utc=pytz.UTC
class Searching_test(LiveServerTestCase):
    def generate_history(self, count, person_list, lab_list, start, end):
        def random_datetime(start, end):
            """
            This function will return a random datetime between two datetime 
            objects.
            """
            start = datetime.strptime(start, '%d/%m/%Y %H:%M') # '1/1/2020 9:00'
            end = datetime.strptime(end, '%d/%m/%Y %H:%M')     # '1/1/2020 9:00'
            delta = end - start
            int_delta = (delta.days * 24 * 60) + (delta.seconds / 60)
            random_minute = randrange(int_delta)
            return start + timedelta(minutes=random_minute)

        class infinite_iterator():    
            def __init__(self,lst):
                self.i = 0
                self.lst = lst
                self.lst_len = len(lst)
            def next(self):        
                result = self.lst[self.i % self.lst_len]
                self.i += 1
                return result

        person_list = infinite_iterator(person_list)

        for i in range(count):
            p = person_list.next()
            checkin_time = random_datetime(start, end)
            checkout_time = checkin_time + timedelta(hours=random.choice([1,2,3]))
            a = History.objects.create( person=p, lab=random.choice(lab_list), checkin=checkin_time, checkout=checkout_time)
            a.checkin=checkin_time
            a.save()

    def setUp(self):
        labA = Lab.objects.create(name="computer", amount=10)
        labB = Lab.objects.create(name="ece", amount=10)
        labC = Lab.objects.create(name="physic", amount=10)
        lablist = [labA, labB, labC]
        
        person_list = []    
        for i in range(25):
            firstname = names.get_first_name() + str(randrange(1000))
            lastname = names.get_last_name()
            u = User.objects.create(username=firstname,email='',password=lastname)
            p = Person.objects.create(user=u, first_name=firstname, last_name=lastname)
            person_list.append(p)
        
        self.generate_history(100, person_list, lablist, "1/1/2020 9:00", "1/1/2020 16:00")
        self.generate_history(100, person_list, lablist, "2/1/2020 9:00", "2/1/2020 16:00")


    def test_can_query_by_name(self):
        pass
    def test_can_query_by_lab_name(self):
        pass
    def test_can_query_by_time_period(self): 
        start = datetime.strptime("2020-1-1T12:00 +0700", "%Y-%m-%dT%H:%M %z")
        stop = datetime.strptime("2020-1-2T12:00 +0700", "%Y-%m-%dT%H:%M %z")
        histories = History.objects.all()
        histories = histories.exclude( Q(checkin__gt=stop) | Q(checkout__lt=start) )
        for h in histories:
            checkin = h.checkin
            checkout = h.checkout
            print(checkin, checkout, start, stop)
            self.assertTrue(
                (checkin >= start and checkin <= stop) # intersect forward
                or (checkout >= start and checkout <= stop) # intersect backward
                or (checkin >= start and checkout <= stop)  # intersect inside
                or (checkin <= start and checkout>= stop)  
            )
    def test_can_search_people_who_close_to_infected_person(self):
        pass
