import datetime
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Ballot, Question, Choice, VoteRecord
from users.models import Profile
from .forms import AddBallotForm, BallotQuestionFormset, QuestionChoiceFormset

class BallotFormTests(TestCase):
    """
    test ballot form labels
    """
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

    def test_ballot_form_due_date(self):
        form = AddBallotForm()
        self.assertTrue(form.fields['due_date'].label is None or form.fields['due_date'].
                        label == 'Due date')

    """
    end label tests
    """

    """
    form validation tests
    """
    def test_ballot_form_pub_past(self):
        """
        forms cannot be published in the past
        """
        date = timezone.now() - datetime.timedelta(days=1)
        form = AddBallotForm(data={'ballot_title': "Test", 'ballot_description': "test", 'pub_date': date,
                                   'due_date': timezone.now() + datetime.timedelta(days=30)})
        self.assertFalse(form.is_valid())

    def test_ballot_form_pub_now(self):
        """
        forms cannot be published now
        """
        date = timezone.now()
        form = AddBallotForm(data={'ballot_title': "Test", 'ballot_description': "test", 'pub_date': date,
                                   'due_date': timezone.now() + datetime.timedelta(days=30)})
        self.assertFalse(form.is_valid())

    def test_ballot_form_pub_future(self):
        """
        forms can be published in the future
        """
        date = timezone.now() + datetime.timedelta(days=1)
        form = AddBallotForm(data={'ballot_title': "Test", 'ballot_description': "test", 'pub_date':date,
                                   'due_date':timezone.now() + datetime.timedelta(days=30)})
        self.assertTrue(form.is_valid())

    def test_ballot_form_pub_after_due(self):
        """
        form publish date must be before form due date
        """
        date = timezone.now() + datetime.timedelta(days=31)
        form = AddBallotForm(data={'ballot_title': "Test", 'ballot_description': "test", 'pub_date':date,
                                   'due_date': timezone.now() + datetime.timedelta(days=30)})
        self.assertFalse(form.is_valid())

    """
    end validation tests
    """