import datetime
from django.contrib.auth.models import User
from django.core.signing import Signer
from django.test import Client, TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from .models import Ballot, Question, Choice, VoteRecord, CastBallot, CastVote
from users.models import Profile

class IndexTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save
        profile = self.user.profile
        profile.ssn = "555-55-5555"
        profile.district = "BaltimoreCounty"
        profile.middle_name = "Jack"
        profile.save()
        self.ballot = Ballot.objects.create(ballot_title="Test", district="BaltimoreCounty", pub_date=timezone.now())
        self.ballot.save()
        signer = Signer()
        self.sign = signer.sign(self.user.profile.sign)
        self.sign = self.sign[51:]

    """index url tests"""
    def test_index_url_exists(self):
        """
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get('/')
        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(response.status_code, 302)

    def test_index_url_reverse(self):
        """
        reverse match should exist
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get(reverse('ballots:index'))
        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(response.status_code, 302)
    def test_index_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        response = self.client.get('/')
        self.assertRedirects(response, '/users/login/')
    def test_index_login(self):
        """if user is logged in displays ballot index page"""
        self.client.force_login(self.user)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    """end url tests"""

    """index queryset tests"""
    def test_district_list(self):
        """
        ballot_list should only contain published ballots with districts matching the user's district
        """
        yesterday = timezone.now() - datetime.timedelta(days=1)
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:index'))

        """list size should be one"""
        self.assertEqual(response.context['ballot_list'].count(), 1)

        wrong_ballot = Ballot(ballot_title="Wrong", district="MontgomeryCounty", pub_date=yesterday)
        wrong_ballot.save()
        response = self.client.get(reverse('ballots:index'))
        """list size should not change"""
        self.assertEqual(response.context['ballot_list'].count(), 1)

        right_ballot = Ballot(ballot_title="Wrong", district=self.user.profile.district, pub_date=yesterday)
        right_ballot.save()
        self.ballot.save()
        response = self.client.get(reverse('ballots:index'))
        """list size should be two"""
        self.assertEqual(response.context['ballot_list'].count(), 2)
        for ballot in response.context['ballot_list']:
            """all ballot districts should match user district"""
            self.assertEqual(response.context['user'].profile.district, ballot.district)

    def test_date_list(self):
        """
        ballot_list should only contain published ballots with districts matching the user's district
        """
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:index'))

        """list size should be one"""
        self.assertEqual(response.context['ballot_list'].count(), 1)

        wrong_ballot = Ballot(ballot_title="Wrong", district=self.user.profile.district, pub_date=tomorrow)
        wrong_ballot.save()
        response = self.client.get(reverse('ballots:index'))
        """list size should not change"""
        self.assertEqual(response.context['ballot_list'].count(), 1)

        right_ballot = Ballot(ballot_title="Wrong", district=self.user.profile.district, pub_date=timezone.now())
        right_ballot.save()
        self.ballot.save()
        response = self.client.get(reverse('ballots:index'))
        """list size should be two"""
        self.assertEqual(response.context['ballot_list'].count(), 2)
        for ballot in response.context['ballot_list']:
            """all ballot districts should match user district"""
            self.assertLessEqual(ballot.pub_date, timezone.now())

    def test_finished_list(self):
        """
        ballot_list should only contain ballots user has not voted on
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:index'))

        """list size should be one"""
        self.assertEqual(response.context['ballot_list'].count(), 1)
        """finished list size should be zero"""
        self.assertEqual(response.context['finished_ballots'].count(), 0)

        finished_ballot = Ballot(ballot_title="Wrong", district=self.user.profile.district, pub_date=timezone.now())
        finished_ballot.save()
        response = self.client.get(reverse('ballots:index'))
        """list size should not change"""
        self.assertEqual(response.context['ballot_list'].count(), 2)
        """finished list size should not change"""
        self.assertEqual(response.context['finished_ballots'].count(), 0)
        vote_record = VoteRecord(voter_signature=self.sign, assoc_ballot=finished_ballot)
        vote_record.save()
        response = self.client.get(reverse('ballots:index'))
        """list size should be one"""
        self.assertEqual(response.context['ballot_list'].count(), 1)
        """finished list size should be one"""
        self.assertEqual(response.context['finished_ballots'].count(), 1)
        for ballot in response.context['ballot_list']:
            """only test ballot should be in this list"""
            self.assertEqual(ballot.ballot_title, "Test")
        for ballot in response.context['finished_ballots']:
            """only wrong ballot should be in this list"""
            self.assertEqual(ballot.ballot_title, "Wrong")
    """end queryset tests"""

class DetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save
        profile = self.user.profile
        profile.ssn = "555-55-5555"
        profile.district = "BaltimoreCounty"
        profile.middle_name = "Jack"
        profile.save()
        self.ballot = Ballot.objects.create(ballot_title="Test", district="BaltimoreCounty", pub_date=timezone.now())
        self.ballot.save()
        signer = Signer()
        self.sign = signer.sign(self.user.profile.sign)
        self.sign = self.sign[51:]

    """detail url tests"""

    def test_detail_url_exists(self):
        """
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': self.ballot.pk}))
        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(response.status_code, 302)

    def test_detail_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': self.ballot.pk}))
        self.assertRedirects(response, '/users/login/')

    def test_detail_login(self):
        """if user is logged in and all validation succeeds displays ballot detail page"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': self.ballot.pk}))
        self.assertEqual(response.status_code, 200)

    def test_detail_district_mismatch(self):
        """if districts do not match raises 403 forbidden"""
        wrong_ballot = Ballot.objects.create(ballot_title="Wrong", district="Moco", pub_date=timezone.now())
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': wrong_ballot.pk}))
        self.assertEqual(response.status_code, 403)

    def test_detail_unpublished(self):
        """if ballot is not published raises 403 forbidden"""
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        wrong_ballot = Ballot.objects.create(ballot_title="Wrong", district="BaltimoreCounty", pub_date=tomorrow)
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': wrong_ballot.pk}))
        self.assertEqual(response.status_code, 403)

    def test_detail_past_due(self):
        """if ballot is not published raises 403 forbidden"""
        yesterday = timezone.now() - datetime.timedelta(days=1)
        last_week = timezone.now() - datetime.timedelta(weeks=1)
        wrong_ballot = Ballot.objects.create(ballot_title="Wrong", district="BaltimoreCounty", pub_date=last_week,
                                             due_date=yesterday)
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': wrong_ballot.pk}))
        self.assertEqual(response.status_code, 403)

    def test_detail_finished_ballot(self):
        wrong_ballot = Ballot.objects.create(ballot_title="Wrong", district="BaltimoreCounty", pub_date=timezone.now())
        vote_record = VoteRecord.objects.create(voter_signature=self.sign, assoc_ballot=wrong_ballot)
        vote_record.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': wrong_ballot.pk}))
        self.assertEqual(response.status_code, 403)
    """end url tests"""

    """detail context tests"""
    def test_detail_ballot(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': self.ballot.pk}))
        self.assertEqual(response.context['ballot'].ballot_title, "Test")

    def test_detail_question_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': self.ballot.pk}))
        """test with 0 questions"""
        self.assertEqual(response.context['question_list'].count(), 0)
        """test with questions"""
        question1 = Question.objects.create(question_text="Q1", ballot=self.ballot)
        question1.save()
        question2 = Question.objects.create(question_text="Q2", ballot=self.ballot)
        question2.save()
        response = self.client.get(reverse('ballots:detail', kwargs={'ballot_id': self.ballot.pk}))
        self.assertEqual(response.context['question_list'].count(), 2)
        """confirm questions are correct"""
        self.assertTrue(response.context['question_list'].filter(question_text="Q1").exists())
        self.assertTrue(response.context['question_list'].filter(question_text="Q2").exists())
    """end context tests"""

class VoteViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', last_name='Smith', username='testuser',
                                        password='password123', email='JohnSmith@gmail.com')
        self.user.save
        profile = self.user.profile
        profile.ssn = "555-55-5555"
        profile.district = "BaltimoreCounty"
        profile.middle_name = "Jack"
        profile.save()
        self.ballot = Ballot.objects.create(ballot_title="Test", district="BaltimoreCounty", pub_date=timezone.now())
        self.ballot.save()
        self.question = Question.objects.create(question_text="Q1", ballot=self.ballot)
        self.question.save()
        self.choice = Choice.objects.create(choice_text="A", question=self.question)
        self.choice.save()
        signer = Signer()
        self.sign = signer.sign(self.user.profile.sign)
        self.sign = self.sign[51:]

    """vote url tests"""

    def test_vote_url_exists(self):
        """
        if url exists shouldn't 404, status code should be 302 due to redirect
        """
        response = self.client.get(reverse('ballots:vote', kwargs={'ballot_id': self.ballot.pk}))
        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(response.status_code, 302)

    def test_vote_anon_redirect(self):
        """
        if no user is logged in redirects to login page
        """
        response = self.client.get(reverse('ballots:vote', kwargs={'ballot_id': self.ballot.pk}))
        self.assertRedirects(response, '/users/login/')

    def test_vote_no_questions(self):
        """if no questions raises 404"""
        wrong_ballot = Ballot.objects.create(ballot_title="Test", district="BaltimoreCounty", pub_date=timezone.now())
        wrong_ballot.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:vote', kwargs={'ballot_id': wrong_ballot.pk}))
        self.assertEqual(response.status_code, 404)

    def test_vote_login(self):
        """if user is logged in and all validation succeeds runs vote
        question needed for vote page"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('ballots:vote', kwargs={'ballot_id': self.ballot.pk}))
        """redirects on success"""
        self.assertEqual(response.status_code, 302)
    """end url tests"""

    """voting behavior tests"""
    def test_vote_successful(self):
        vote_records = VoteRecord.objects.all()
        # Should not exist yet
        self.assertEqual(vote_records.count(), 0)

        cast_ballots = CastBallot.objects.filter(assoc_ballot=self.ballot)
        # Should not exist yet
        self.assertFalse(cast_ballots.exists())

        cast_votes = CastVote.objects.filter(choice=self.choice)
        # should not exist yet
        self.assertFalse(cast_votes.exists())

        self.client.force_login(self.user)
        response = self.client.post(reverse('ballots:vote', kwargs={'ballot_id': self.ballot.pk}),
                                     {self.question.question_text: self.choice.pk})

        vote_records = VoteRecord.objects.all()
        #Should create vote record
        self.assertEqual(vote_records.count(), 1)

        cast_ballots = CastBallot.objects.filter(assoc_ballot=self.ballot)
        #Should create cast ballot
        self.assertTrue(cast_ballots.exists())

        cast_votes = CastVote.objects.filter(choice=self.choice)
        #should create a cast vote
        self.assertTrue(cast_votes.exists())

    def test_vote_none_selected(self):
        vote_records = VoteRecord.objects.filter(voter_signature=self.sign)
        # Should not exist yet
        self.assertFalse(vote_records.exists())

        cast_ballots = CastBallot.objects.filter(assoc_ballot=self.ballot)
        # Should not exist yet
        self.assertFalse(cast_ballots.exists())

        cast_votes = CastVote.objects.filter(choice=self.choice)
        # should not exist yet
        self.assertFalse(cast_votes.exists())

        self.client.force_login(self.user)
        response = self.client.post(reverse('ballots:vote', kwargs={'ballot_id': self.ballot.pk}), {})

        vote_records = VoteRecord.objects.all()
        #Should create vote record
        self.assertEqual(vote_records.count(), 0)

        cast_ballots = CastBallot.objects.filter(assoc_ballot=self.ballot)
        #Should create cast ballot
        self.assertFalse(cast_ballots.exists())

        cast_votes = CastVote.objects.filter(choice=self.choice)
        #should create a cast vote
        self.assertFalse(cast_votes.exists())

    def test_vote_wrong_district(self):
        wrong_ballot = Ballot.objects.create(ballot_title="Wrong", district="Moco", pub_date=timezone.now())
        wrong_ballot.save()
        question1 = Question.objects.create(question_text="Q1", ballot=wrong_ballot)
        question1.save()
        choice1 = Choice.objects.create(choice_text="A", question=question1)
        choice1.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse('ballots:vote', kwargs={'ballot_id':wrong_ballot.pk}),
                                    {question1.question_text: choice1.pk})

        vote_records = VoteRecord.objects.all()
        # Should not create vote record
        self.assertEqual(vote_records.count(), 0)

        cast_ballots = CastBallot.objects.filter(assoc_ballot=self.ballot)
        # Should not create cast ballot
        self.assertFalse(cast_ballots.exists())

        cast_votes = CastVote.objects.filter(choice=self.choice)
        # should not create a cast vote
        self.assertFalse(cast_votes.exists())

    def test_vote_not_published(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        wrong_ballot = Ballot.objects.create(ballot_title="Wrong", district="BaltimoreCounty", pub_date=tomorrow)
        wrong_ballot.save()
        question1 = Question.objects.create(question_text="Q1", ballot=wrong_ballot)
        question1.save()
        choice1 = Choice.objects.create(choice_text="A", question=question1)
        choice1.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse('ballots:vote', kwargs={'ballot_id': wrong_ballot.pk}),
                                    {question1.question_text: choice1.pk})

        vote_records = VoteRecord.objects.all()
        # Should not create vote record
        self.assertEqual(vote_records.count(), 0)

        cast_ballots = CastBallot.objects.filter(assoc_ballot=self.ballot)
        # Should not create cast ballot
        self.assertFalse(cast_ballots.exists())
        cast_votes = CastVote.objects.filter(choice=self.choice)
        # should not create a cast vote
        self.assertFalse(cast_votes.exists())

    def test_vote_past_due(self):
        yesterday = timezone.now() - datetime.timedelta(days=1)
        wrong_ballot = Ballot.objects.create(ballot_title="Wrong", district="BaltimoreCounty", due_date=yesterday)
        wrong_ballot.save()
        question1 = Question.objects.create(question_text="Q1", ballot=wrong_ballot)
        question1.save()
        choice1 = Choice.objects.create(choice_text="A", question=question1)
        choice1.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse('ballots:vote', kwargs={'ballot_id': wrong_ballot.pk}),
                                    {question1.question_text: choice1.pk})

        vote_records = VoteRecord.objects.all()
        # Should not create vote record
        self.assertEqual(vote_records.count(), 0)

        cast_ballots = CastBallot.objects.filter(assoc_ballot=self.ballot)
        # Should not create cast ballot
        self.assertFalse(cast_ballots.exists())

        cast_votes = CastVote.objects.filter(choice=self.choice)
        # should not create a cast vote
        self.assertFalse(cast_votes.exists())

    def test_vote_finished(self):
        wrong_ballot = Ballot.objects.create(ballot_title="Wrong", district="BaltimoreCounty", pub_date=timezone.now())
        wrong_ballot.save()
        question1 = Question.objects.create(question_text="Q1", ballot=wrong_ballot)
        question1.save()
        vote_record = VoteRecord.objects.create(voter_signature=self.sign, assoc_ballot=wrong_ballot)
        vote_record.save()
        choice1 = Choice.objects.create(choice_text="A", question=question1)
        choice1.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse('ballots:vote', kwargs={'ballot_id': wrong_ballot.pk}),
                                    {question1.question_text: choice1.pk})

        vote_records = VoteRecord.objects.all()
        # Should already exist
        self.assertEqual(vote_records.count(), 1)

        cast_ballots = CastBallot.objects.filter(assoc_ballot=wrong_ballot)
        # Should not create cast ballot
        self.assertFalse(cast_ballots.exists())

        cast_votes = CastVote.objects.filter(choice=choice1)
        # should not create a cast vote
        self.assertFalse(cast_votes.exists())

    def test_vote_finished_other_ballot(self):
        wrong_ballot = Ballot.objects.create(ballot_title="Wrong", district="BaltimoreCounty", pub_date=timezone.now())
        wrong_ballot.save()
        question1 = Question.objects.create(question_text="Q1", ballot=wrong_ballot)
        question1.save()
        vote_record = VoteRecord.objects.create(voter_signature=self.sign, assoc_ballot=self.ballot)
        vote_record.save()
        choice1 = Choice.objects.create(choice_text="A", question=question1)
        choice1.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse('ballots:vote', kwargs={'ballot_id': wrong_ballot.pk}),
                                    {question1.question_text: choice1.pk})

        vote_records = VoteRecord.objects.filter(voter_signature=self.sign).filter(assoc_ballot=wrong_ballot)
        # Should create a new vote record
        self.assertTrue(vote_records.exists())

        cast_ballots = CastBallot.objects.filter(assoc_ballot=wrong_ballot)
        #Should create cast ballot
        self.assertTrue(cast_ballots.exists())

        cast_votes = CastVote.objects.filter(choice=choice1)
        # should not create a cast vote
        self.assertTrue(cast_votes.exists())
