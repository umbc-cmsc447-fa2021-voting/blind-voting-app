import datetime
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from .models import Ballot
from users.models import Profile
from .forms import AddBallotForm

class BallotModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(first_name='John', last_name='Smith', username = 'testuser', password='12345')
        profile = User.profile
        profile.ssn = "555-55-5555"
        profile.district = "BaltimoreCounty"
        profile.middle_name = "Jack"

    def test_was_published_recently_with_future_ballot(self):
        """
        was_published_recently() returns False for ballots whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_ballot = Ballot(pub_date=time)
        self.assertIs(future_ballot.was_published_recently(), False)

    def test_was_published_recently_with_old_ballot(self):
        """
        was_published_recently() returns False for ballots whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_ballot = Ballot(pub_date=time)
        self.assertIs(old_ballot.was_published_recently(), False)

    def test_was_published_recently_with_recent_ballot(self):
        """
        was_published_recently() returns True for ballots whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_ballot = Ballot(pub_date=time)
        self.assertIs(recent_ballot.was_published_recently(), True)

    """
    might want to add a test to make sure the due date of the ballot is after
    the publish. Don't want a ballot to be past due as soon as it is created
    """

class BallotFormTests(TestCase):
    def test_ballot_form_title(self):
        form = AddBallotForm()
        self.assertTrue(form.fields['ballot_title'].label is None or form.fields['ballot_title'].
                        label == 'Ballot title')

    def test_ballot_form_description(self):
        form = AddBallotForm()
        self.assertTrue(form.fields['ballot_description'].label is None or form.fields['ballot_description'].
                        label == 'Ballot description')

    def test_ballot_form_district(self):
        form = AddBallotForm()
        self.assertTrue(form.fields['ballot_description'].label is None or form.fields['district'].
                        label == 'District')

    def test_ballot_form_pub_date(self):
        form = AddBallotForm()
        self.assertTrue(form.fields['pub_date'].label is None or form.fields['pub_date'].
                        label == 'Date published')

    def test_ballot_form_description(self):
        form = AddBallotForm()
        self.assertTrue(form.fields['due_date'].label is None or form.fields['due_date'].
                        label == 'Due date')

class BallotAdminTests(TestCase):
    def test_admin_url_exists(self):
        response = self.client.get('/ballot-admin')
        self.assertEqual(response.status_code, 200)

    def test_admin_url_reverse(self):
        response = self.client.get(reverse('ballots:ballot-admin'))
        self.assertEqual(response.status_code, 200)

class BallotAddTests(TestCase):
    def test_add_url_exists(self):
        response = self.client.get('/add/')
        self.assertEqual(response.status_code, 200)

    def test_admin_url_reverse(self):
        response = self.client.get(reverse('ballots:add'))
        self.assertEqual(response.status_code, 200)

