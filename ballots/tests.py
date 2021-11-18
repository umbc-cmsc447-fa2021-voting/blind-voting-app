import datetime
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from .models import Ballot, Question, Choice
from users.models import Profile
from .forms import AddBallotForm, BallotQuestionFormset, QuestionChoiceFormset

class BallotModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save
        profile = self.user.profile
        profile.ssn = "555-55-5555"
        profile.district = "BaltimoreCounty"
        profile.middle_name = "Jack"
        self.ballot = Ballot.objects.create(ballot_title="Test", district="BaltimoreCounty")


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

    def test_district_matches(self):
        wrong_ballot = Ballot(ballot_title="Wrong", district="MontgomeryCounty")
        wrong_ballot.save()
        self.ballot.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:index'))
        for ballot in response.context['ballot_list']:
            self.assertEqual(response.context['user'].profile.district, ballot.district)
        #self.assertEqual(test_ballot.district, self.user.profile.district)

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

    def test_ballot_form_due_date(self):
        form = AddBallotForm()
        self.assertTrue(form.fields['due_date'].label is None or form.fields['due_date'].
                        label == 'Due date')

    def test_ballot_form_pub_past(self):
        date = timezone.now() - datetime.timedelta(days=1)
        form = AddBallotForm(data={'ballot_title': "Test", 'ballot_description': "test", 'pub_date': date,
                                   'due_date': timezone.now() + datetime.timedelta(days=30)})
        self.assertFalse(form.is_valid())

    def test_ballot_form_pub_now(self):
        date = timezone.now()
        form = AddBallotForm(data={'ballot_title': "Test", 'ballot_description': "test", 'pub_date': date,
                                   'due_date': timezone.now() + datetime.timedelta(days=30)})
        self.assertFalse(form.is_valid())

    def test_ballot_form_pub_future(self):
        date = timezone.now() + datetime.timedelta(days=1)
        form = AddBallotForm(data={'ballot_title': "Test", 'ballot_description': "test", 'pub_date':date,
                                   'due_date':timezone.now() + datetime.timedelta(days=30)})
        self.assertTrue(form.is_valid())

    def test_ballot_form_pub_after_due(self):
        date = timezone.now() + datetime.timedelta(days=31)
        form = AddBallotForm(data={'ballot_title': "Test", 'ballot_description': "test", 'pub_date':date,
                                   'due_date':timezone.now() + datetime.timedelta(days=30)})
        self.assertFalse(form.is_valid())

class BallotAdminTests(TestCase):
    def test_admin_url_exists(self):
        response = self.client.get('/ballot-admin')
        self.assertNotEqual(response.status_code, 404)

    def test_admin_url_reverse(self):
        response = self.client.get(reverse('ballots:ballot-admin'))
        self.assertNotEqual(response.status_code, 404)

class PublishedBallotsTests(TestCase):
    def test_published_url_exists(self):
        response = self.client.get('/ballot-admin/published')
        self.assertNotEqual(response.status_code, 404)

    def test_published_url_reverse(self):
        response = self.client.get(reverse('ballots:published'))
        self.assertNotEqual(response.status_code, 404)

class BallotAddTests(TestCase):
    def test_add_url_exists(self):
        response = self.client.get('/add/')
        self.assertNotEqual(response.status_code, 404)

    def test_add_url_reverse(self):
        response = self.client.get(reverse('ballots:add'))
        self.assertNotEqual(response.status_code, 404)

class BallotEditTests(TestCase):
    def setUp(self):
        self.ballot = Ballot.objects.create(ballot_title="Test")

    def test_edit_url_exists(self):
        url = reverse('ballots:edit', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

class AddQuestionTests(TestCase):
    def setUp(self):
        self.ballot = Ballot.objects.create(ballot_title="Test")

    def test_question_url_exists(self):
        url = reverse('ballots:questions', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

class AddChoiceTests(TestCase):
    def setUp(self):
        self.ballot = Ballot.objects.create(ballot_title="Test")
        self.question = Question.objects.create(question_text="Test", ballot_id=self.ballot.id)

    def test_choice_url_exists(self):
        url = reverse('ballots:choices', kwargs={'pk': self.question.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)