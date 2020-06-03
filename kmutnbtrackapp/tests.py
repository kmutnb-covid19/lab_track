import datetime
import time
import json
import requests

from django.test import TestCase
from django.test import LiveServerTestCase
from django.test import Client
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from kmutnbtrackapp.models import History, Person, Lab
# Create your tests here.

class Searching_test(LiveServerTestCase):

    def setUp(self):
        pass
    
    def test_can_query_by_name(self):
        pass
    def test_can_query_by_lab_name(self):
        pass
    def test_can_query_by_time_period(self):
        pass

    def test_can_search_people_who_close_to_infected_person(self):
        pass