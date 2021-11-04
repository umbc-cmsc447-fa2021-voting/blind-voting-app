import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import Ballot
from users.models import Profile

class BallotModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(first_name='John', last_name='Smith')
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

    def test_districts_match(self):
        """
        users should only see ballots that match their district
        therefore the district field of both models should be comparable
        """
        user = User.objects.get(id=1)
        test_ballot = Ballot()
        test_ballot.district="BaltimoreCounty"
        self.assertEqual(test_ballot.district, user.profile.district)

    """
    might want to add a test to make sure the due date of the ballot is after
    the publish. Don't want a ballot to be past due as soon as it is created
    """