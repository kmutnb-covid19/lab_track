from django.test import LiveServerTestCase, TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
from kmutnbtrackapp.models import *
from datetime import datetime
import time



class LoginTest(LiveServerTestCase):

    port = 8001

    def setUp(self):
        self.browser = webdriver.Firefox()
        super_user = User.objects.create_superuser(username="0", password="0")
        lab_com = Lab.objects.create(name="Computer Lab",amount=10)

        self.lab_com_hash = lab_com.hash

    def tearDown(self):
        self.browser.quit()

    '''

    def test_admin_login(self):
        self.browser.get(self.live_server_url + "/admin")
        time.sleep(1)

        username = self.browser.find_element_by_id("id_username")
        username.send_keys("0")
        time.sleep(1)

        password = self.browser.find_element_by_id("id_password")
        password.send_keys("0")

        password.send_keys(Keys.ENTER)
        time.sleep(1)

    def test_sign_in_with_gmail(self):
        self.browser.get(self.live_server_url + "/lab/" + str(self.lab_com_hash))
        time.sleep(1)

        google_button = self.browser.find_element_by_id("google_sign_in_button")
        google_button.click()
        time.sleep(5)

        username = self.browser.find_element_by_id("identifierId")
        username.send_keys("functionaltest172@gmail.com")
        time.sleep(5)

        username.send_keys(Keys.ENTER)
        time.sleep(5)

        password = self.browser.find_element_by_name("password")
        password.send_keys('Djangotest123')
        time.sleep(5)

        password.send_keys(Keys.ENTER)
        time.sleep(5)

        room = self.browser.find_element_by_id('room_name').text
        self.assertIn('Computer Lab', room)
        '''

    def test_user_can_check_in(self):
        self.browser.get(self.live_server_url + "/lab/" + str(self.lab_com_hash))
        time.sleep(10)

        google_button = self.browser.find_element_by_id("google_sign_in_button")
        google_button.click()
        time.sleep(10)

        username = self.browser.find_element_by_id("identifierId")
        username.send_keys("functionaltest172@gmail.com")
        time.sleep(10)

        username.send_keys(Keys.ENTER)
        time.sleep(10)

        password = self.browser.find_element_by_name("password")
        password.send_keys('Djangotest123')
        time.sleep(10)

        password.send_keys(Keys.ENTER)
        time.sleep(10)

        room = self.browser.find_element_by_id('room_name').text
        self.assertIn('Computer Lab', room)

        self.browser.find_element_by_xpath("//select[@name='check_out_select_time']/option[text()='อื่นๆ']").click()
        time.sleep(10)

        time_check_out = self.browser.find_element_by_name("check_out_time")
        time_check_out.send_keys("23:59")
        time.sleep(10)

        check_in_button = self.browser.find_element_by_id('check_in_button').click()
        time.sleep(10)

        check_out_time = self.browser.find_element_by_id('check_out_time_id').text
        self.assertIn('11:59 PM', check_out_time)







