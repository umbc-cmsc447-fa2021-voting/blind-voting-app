import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Ballot

class BallotArchiveTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            first_name='John', 
            last_name='Smith',
            username='testuser',
            password='password123', 
            email='JohnSmith@gmail.com'
        )
        self.user.save

    """
    archived ballots url tests
    """
    def test_archive_url_exists(self):
        """
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get('/ballot-admin/archived')
        self.assertNotEqual(response.status_code, 404)

    def test_archive_url_reverse(self):
        """
        reverse match should exist
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get(reverse('ballots:archived'))
        self.assertNotEqual(response.status_code, 404)

    def test_archive_non_staff_redirect(self):
        """
        if non admin is logged in redirects to ballot index
        """
        self.client.force_login(self.user)
        response = self.client.get('/ballot-admin/archived')
        self.assertRedirects(response, '/')

    def test_archive_staff_access(self):
        """
        if admin is logged in response succeeds
        """
        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)
        response = self.client.get('/ballot-admin/archived')
        self.assertEqual(response.status_code, 200)

    def test_archived_list(self):
        """
        published should only show published ballots
        adding one ballot with a due date older than one year should return one ballot
        """
        old_ballot = Ballot(
            ballot_title="Old",
            pub_date=timezone.now() - datetime.timedelta(days=400),
            due_date=timezone.now() - datetime.timedelta(days=390)
        )
        old_ballot.save()

        new_ballot = Ballot(
            ballot_title="New",
            pub_date=timezone.now() + datetime.timedelta(days=1),
            due_date=timezone.now() + datetime.timedelta(days=2)
        )
        new_ballot.save()

        pub_ballot = Ballot(ballot_title="Pub", pub_date=timezone.now())
        pub_ballot.save()

        admin = User.objects.create_superuser('testadmin', 'a@a.com', 'pass123')
        self.client.force_login(admin)

        response = self.client.get('/ballot-admin/archived')
        self.assertEqual(len(response.context['ballots']), 1)