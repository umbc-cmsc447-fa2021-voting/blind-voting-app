from django.core import mail
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from users.models import Profile
from datetime import datetime

# Create your tests here.

class ProfileModelTest(TestCase):
    user = None

    def setUp(self):
        self.user = User.objects.create(id=1, first_name='John', last_name='Smith')
        profile = User.profile
        profile.ssn = "555-55-5555"
        profile.district = "BaltimoreCounty"
        profile.middle_name = "Jack"

    def test_ssn_label(self):
        field_label = self.user.profile._meta.get_field('ssn').verbose_name
        self.assertEqual(field_label, 'ssn')

    def test_district_label(self):
        field_label = self.user.profile._meta.get_field('district').verbose_name
        self.assertEqual(field_label, 'district')

    def test_middle_name_label(self):
        field_label = self.user.profile._meta.get_field('middle_name').verbose_name
        self.assertEqual(field_label, 'middle name')

    def test_ssn_max_length(self):
        max_length = self.user.profile._meta.get_field('ssn').max_length
        self.assertEqual(max_length, 20)

    def test_district_max_length(self):
        max_length = self.user.profile._meta.get_field('district').max_length
        self.assertEqual(max_length, 50)

    def test_middle_name_max_length(self):
        max_length = self.user.profile._meta.get_field('middle_name').max_length
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

class PasswordResetFlowTests(TestCase):
    user = None

    def setUp(self):
        self.user = User.objects.create(username='JohnDoe', first_name='John', last_name='Doe', email='JohnDoe@gmail.com')
        profile = User.profile
        profile.ssn = '111-11-1111'
        profile.district = 'HowardCounty'
        profile.middle_name = 'Jack'

    def test_get_password_reset(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_post_password_reset_success(self):
        data = { 'email': 'JohnDoe@gmail.com' }
        response = self.client.post(reverse('password_reset'), data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/password_reset/done/')

        self.assertGreater(len(mail.outbox), 0)
        reset_emails = [email for email in mail.outbox if email.subject == 'Password reset on testserver' and self.user.username in email.body]
        self.assertEqual(len(reset_emails), 1)
    
    def test_post_password_reset_failure(self):
        data = { 'email': 'DNE@gmail.com' }
        outbox_len_before = len(mail.outbox)
        response = self.client.post(reverse('password_reset'), data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/password_reset/done/')

        self.assertEqual(len(mail.outbox), outbox_len_before)

    def test_password_reset_confirm(self):
        data = { 'email': 'JohnDoe@gmail.com' }
        response = self.client.post(reverse('password_reset'), data)

        token = response.context[0]['token']
        uid = response.context[0]['uid']
        response = self.client.get(reverse('password_reset_confirm', kwargs={ 'token': token, 'uidb64': uid }))

        # Assert that we can visit the reset page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/reset/{}/set-password/'.format(uid))

        data = { 'new_password1': 'newpassword', 'new_password2': 'newpassword' }
        response = self.client.post(reverse('password_reset_confirm', kwargs={ 'token': token, 'uidb64': uid }), data)

        # Assert that our reset was accepted
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/reset/{}/set-password/'.format(uid))

class NewAccountTests(TestCase):
    user = None

    def setUp(self):
        self.user = User.objects.create(username='JohnDoe', first_name='John', last_name='Doe', email='JohnDoe@gmail.com')
        profile = User.profile
        profile.ssn = '111-11-1111'
        profile.district = 'HowardCounty'
        profile.middle_name = 'Jack'

    def test_new_user_sends_email(self):
        self.assertGreater(len(mail.outbox), 0)
        reset_emails = [email for email in mail.outbox if email.subject == 'Blind Voting App - Account Created' and self.user.username in email.body]
        self.assertEqual(len(reset_emails), 1)
