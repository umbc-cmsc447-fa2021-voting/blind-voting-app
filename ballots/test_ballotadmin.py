import datetime
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Ballot, Question, Choice, VoteRecord
from users.models import Profile
from .forms import AddBallotForm, BallotQuestionFormset, QuestionChoiceFormset

class BallotAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@fakemail.com')
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
                                        password='password123', email='JohnSmith@fakemail.com')
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
                                        password='password123', email='JohnSmith@fakemail.com')
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
        old_ballot = Ballot(
            ballot_title="Old", 
            pub_date=timezone.now() - datetime.timedelta(days=2),
            due_date=timezone.now() - datetime.timedelta(days=1)
        )
        old_ballot.save()

        too_old_ballot = Ballot(
            ballot_title="Too Old", 
            pub_date=timezone.now() - datetime.timedelta(days=400),
            due_date=timezone.now() - datetime.timedelta(days=390)
        )
        too_old_ballot.save()

        new_ballot = Ballot(
            ballot_title="New", 
            pub_date=timezone.now() + datetime.timedelta(days=1)
        )
        new_ballot.save()
        
        pub_ballot = Ballot(ballot_title="New", pub_date=timezone.now())
        pub_ballot.save()

        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')

        self.client.force_login(admin)
        response = self.client.get('/ballot-admin/published')
        self.assertEqual(len(response.context['ballots']), 1)

class BallotAddTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@fakemail.com')
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
                                        password='password123', email='JohnSmith@fakemail.com')
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
                                        password='password123', email='JohnSmith@fakemail.com')
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
                                        password='password123', email='JohnSmith@fakemail.com')
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
                                        password='password123', email='JohnSmith@fakemail.com')
        self.user.save

    """
    edit choice url tests
    """
    def test_detail_url_exists(self):
        url = reverse('ballots:ballot-detail', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

    def test_detail_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        url = reverse('ballots:ballot-detail', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/users/login/')

    def test_detail_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        url = reverse('ballots:ballot-detail', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/')

    def test_detail_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        url = reverse('ballots:ballot-detail', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    """
    end url tests
    """

class BallotDeleteTests(TestCase):
    def setUp(self):
        self.ballot = Ballot.objects.create(ballot_title="Test")
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save

    """
    edit choice url tests
    """
    def test_delete_url_exists(self):
        url = reverse('ballots:delete', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

    def test_delete_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        url = reverse('ballots:delete', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/users/login/')

    def test_delete_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        url = reverse('ballots:delete', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/')

    def test_delete_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        url = reverse('ballots:delete', kwargs={'pk': self.ballot.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_old_ballot(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        old_ballot = Ballot.objects.create(ballot_title="Test", pub_date=timezone.now()-datetime.timedelta(days=1))
        url = reverse('ballots:delete', kwargs={'pk': old_ballot.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '/ballot-admin')
    """
    end url tests
    """
    def test_delete_function(self):
        """
        ballot should be removed from ballot objects
        """
        self.assertEqual(Ballot.objects.all().count(), 1)
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        url = reverse('ballots:delete', kwargs={'pk': self.ballot.pk})
        response = self.client.post(url)
        self.assertEqual(Ballot.objects.all().count(), 0)
        self.assertEqual(response.status_code, 302)