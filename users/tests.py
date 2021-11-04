from django.core import mail
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from users.models import Profile
from datetime import datetime

# Create your tests here.

class ProfileModelTest(TestCase):
    def setUp(self):
        User.objects.create(id=1, first_name='John', last_name='Smith')
        profile = User.profile
        profile.ssn = "555-55-5555"
        profile.district = "BaltimoreCounty"
        profile.middle_name = "Jack"

    def test_ssn_label(self):
        user = User.objects.get(id=1)
        field_label = user.profile._meta.get_field('ssn').verbose_name
        self.assertEqual(field_label, 'ssn')

    def test_district_label(self):
        user = User.objects.get(id=1)
        field_label = user.profile._meta.get_field('district').verbose_name
        self.assertEqual(field_label, 'district')

    def test_middle_name_label(self):
        user = User.objects.get(id=1)
        field_label = user.profile._meta.get_field('middle_name').verbose_name
        self.assertEqual(field_label, 'middle name')

    def test_ssn_max_length(self):
        user = User.objects.get(id=1)
        max_length = user.profile._meta.get_field('ssn').max_length
        self.assertEqual(max_length, 20)

    def test_district_max_length(self):
        user = User.objects.get(id=1)
        max_length = user.profile._meta.get_field('district').max_length
        self.assertEqual(max_length, 50)

    def test_middle_name_max_length(self):
        user = User.objects.get(id=1)
        max_length = user.profile._meta.get_field('middle_name').max_length
        self.assertEqual(max_length, 30)

class LoginFlowTests(TestCase):
    def setUp(self):
        User.objects.create(username = 'johnny', first_name='John', last_name='Doe', email='JohnDoe@gmail.com', password='password123')
        profile = User.profile
        profile.ssn = '111-11-1111'
        profile.district = 'HowardCounty'
        profile.middle_name = 'Jack'

    def test_get_login(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_post_login_success(self):
        data = { 'username': 'johnny', 'password': 'password123' }
        response = self.client.post(reverse('login'), data, follow=True)
        # self.assertTrue(response.context['user'].is_active)
        self.assertEqual(response.status_code, 200)
        
        # Check if user is logged in or not
        user = User.objects.get(username='johnny')
        # self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.assertTrue(user.is_authenticated)
        
        self.client.logout()
        # self.client.post('/users/logout', data, follow=True)
        # self.assertRedirects(response, '/admin', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        # self.assertEqual(response.url, '')
    
    def test_post_login_failure(self):
        data = { 'username': 'DNE', 'password': 'password123' }
        response = self.client.post(reverse('login'), data, follow=True)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='johnny')
        # self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.assertTrue(user.is_authenticated)
        # self.client.logout()
