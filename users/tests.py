from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Profile
from datetime import datetime
# Create your tests here.


class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(first_name='John', last_name='Smith')
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