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
        self.ballot = Ballot.objects.create(ballot_title="Test", district="BaltimoreCounty", pub_date=timezone.now())


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
        makes sure the due date of the ballot is after the publish.
        Don't want a ballot to be past due as soon as it is created.
        Fixed by clean function in models.py
        """

    def test_district_matches(self):
        """
        ballot_list should only contain published ballots with districts matching the user's district
        """
        wrong_ballot = Ballot(ballot_title="Wrong", district="MontgomeryCounty", pub_date=timezone.now())
        wrong_ballot.save()
        self.ballot.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:index'))
        for ballot in response.context['ballot_list']:
            self.assertEqual(response.context['user'].profile.district, ballot.district)


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

class BallotAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save

    """
    ballot admin url tests
    """
    def test_admin_url_exists(self):
        """
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get('/ballot-admin')
        self.assertNotEqual(response.status_code, 404)

    def test_admin_url_reverse(self):
        """
        reverse match should exist
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get(reverse('ballots:ballot-admin'))
        self.assertNotEqual(response.status_code, 404)

    def test_admin_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        response = self.client.get('/ballot-admin')
        self.assertRedirects(response, '/users/login/')

    def test_admin_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        response = self.client.get('/ballot-admin')
        self.assertRedirects(response, '/')

    def test_admin_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        response = self.client.get('/ballot-admin')
        self.assertEqual(response.status_code, 200)

    """
    end url tests
    """

    def test_admin_list(self):
        """
        ballot admin should only show unpublished ballots
        adding one ballot with pub date in future and one in past should leave list with only one entry
        """
        old_ballot = Ballot(ballot_title="Old", pub_date=timezone.now() - datetime.timedelta(days=1))
        new_ballot = Ballot(ballot_title="New", pub_date=timezone.now() + datetime.timedelta(days=1))
        old_ballot.save()
        new_ballot.save()
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        self.client.force_login(admin)
        response = self.client.get('/ballot-admin')
        self.assertEqual(len(response.context['ballots']), 1)

class PublishedBallotsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save

    """
    published ballots url tests
    """
    def test_published_url_exists(self):
        """
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get('/ballot-admin/published')
        self.assertNotEqual(response.status_code, 404)

    def test_published_url_reverse(self):
        """
        reverse match should exist
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get(reverse('ballots:published'))
        self.assertNotEqual(response.status_code, 404)

    def test_published_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        response = self.client.get('/ballot-admin/published')
        self.assertRedirects(response, '/users/login/')

    def test_published_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        response = self.client.get('/ballot-admin/published')
        self.assertRedirects(response, '/')

    def test_published_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        response = self.client.get('/ballot-admin/published')
        self.assertEqual(response.status_code, 200)

    """
    end url tests
    """

    def test_published_list(self):
        """
        published should only show published ballots
        adding one ballot with pub date in future and one in past should leave list with only one entry
        """
        old_ballot = Ballot(ballot_title="Old", pub_date=timezone.now() - datetime.timedelta(days=2),
                            due_date=timezone.now() - datetime.timedelta(days=1))
        new_ballot = Ballot(ballot_title="New", pub_date=timezone.now() + datetime.timedelta(days=1))
        pub_ballot = Ballot(ballot_title="New", pub_date=timezone.now())
        old_ballot.save()
        new_ballot.save()
        pub_ballot.save()
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        self.client.force_login(admin)
        response = self.client.get('/ballot-admin/published')
        self.assertEqual(len(response.context['ballots']), 1)

class PastBallotsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save

    """
    published ballots url tests
    """
    def test_past_url_exists(self):
        """
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get('/ballot-admin/past')
        self.assertNotEqual(response.status_code, 404)

    def test_past_url_reverse(self):
        """
        reverse match should exist
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get(reverse('ballots:past'))
        self.assertNotEqual(response.status_code, 404)

    def test_past_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        response = self.client.get('/ballot-admin/past')
        self.assertRedirects(response, '/users/login/')

    def test_past_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        response = self.client.get('/ballot-admin/past')
        self.assertRedirects(response, '/')

    def test_past_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        response = self.client.get('/ballot-admin/past')
        self.assertEqual(response.status_code, 200)

    """
    end url tests
    """

    def test_published_list(self):
        """
        published should only show published ballots
        adding one ballot with pub date in future and one in past should leave list with only one entry
        """
        old_ballot = Ballot(ballot_title="Old", pub_date=timezone.now() - datetime.timedelta(days=2),
                            due_date=timezone.now() - datetime.timedelta(days=1))
        new_ballot = Ballot(ballot_title="New", pub_date=timezone.now() + datetime.timedelta(days=1))
        pub_ballot = Ballot(ballot_title="New", pub_date=timezone.now())
        old_ballot.save()
        new_ballot.save()
        pub_ballot.save()
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        self.client.force_login(admin)
        response = self.client.get('/ballot-admin/published')
        self.assertEqual(len(response.context['ballots']), 1)

class BallotAddTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save

    """
    add ballot url tests
    """
    def test_add_url_exists(self):
        """
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get('/add/')
        self.assertNotEqual(response.status_code, 404)

    def test_add_url_reverse(self):
        """
        reverse match should exist
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get(reverse('ballots:add'))
        self.assertNotEqual(response.status_code, 404)

    def test_add_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        response = self.client.get('/add/')
        self.assertRedirects(response, '/users/login/')

    def test_add_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        response = self.client.get('/add/')
        self.assertRedirects(response, '/')

    def test_add_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        response = self.client.get('/add/')
        self.assertEqual(response.status_code, 200)

    """
    end url tests
    """

class BallotEditTests(TestCase):

    def setUp(self):
        self.ballot = Ballot.objects.create(ballot_title="Test")
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save

    """
    edit ballot url tests
    """
    def test_edit_url_exists(self):
        """
        reverse match should exist
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        url = reverse('ballots:edit', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

    def test_edit_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        url = reverse('ballots:edit', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/users/login/')

    def test_edit_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        url = reverse('ballots:edit', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/')

    def test_edit_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        url = reverse('ballots:edit', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_old_ballot(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        old_ballot = Ballot.objects.create(ballot_title="Test", pub_date=timezone.now()-datetime.timedelta(days=1))
        url = reverse('ballots:edit', kwargs={'pk':old_ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/ballot-admin')

    """
    end url tests
    """

class AddQuestionTests(TestCase):
    def setUp(self):
        self.ballot = Ballot.objects.create(ballot_title="Test")
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save

    """
    edit question url tests
    """
    def test_question_url_exists(self):
        url = reverse('ballots:questions', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

    def test_question_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        url = reverse('ballots:questions', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/users/login/')

    def test_question_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        url = reverse('ballots:questions', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/')

    def test_question_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        url = reverse('ballots:questions', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_question_old_ballot(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        old_ballot = Ballot.objects.create(ballot_title="Test", pub_date=timezone.now()-datetime.timedelta(days=1))
        url = reverse('ballots:questions', kwargs={'pk': old_ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/ballot-admin')
    """
    end url tests
    """

class AddChoiceTests(TestCase):
    def setUp(self):
        self.ballot = Ballot.objects.create(ballot_title="Test")
        self.question = Question.objects.create(question_text="Test", ballot_id=self.ballot.id)
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save

    """
    edit choice url tests
    """
    def test_choice_url_exists(self):
        url = reverse('ballots:choices', kwargs={'pk': self.question.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

    def test_choice_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        url = reverse('ballots:choices', kwargs={'pk': self.question.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/users/login/')

    def test_question_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        url = reverse('ballots:choices', kwargs={'pk': self.question.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/')

    def test_question_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        url = reverse('ballots:choices', kwargs={'pk': self.question.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_question_old_ballot(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        old_ballot = Ballot.objects.create(ballot_title="Test", pub_date=timezone.now()-datetime.timedelta(days=1))
        old_question = Question.objects.create(question_text="Test", ballot_id=old_ballot.id)
        url = reverse('ballots:choices', kwargs={'pk': old_question.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/ballot-admin')
    """
    end url tests
    """

class BallotDetailTests(TestCase):
    def setUp(self):
        self.ballot = Ballot.objects.create(ballot_title="Test")
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save

    """
    edit choice url tests
    """
    def test_detail_url_exists(self):
        url = reverse('ballots:ballot-detail', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)
    """
    end url tests
    """
