import datetime

from django.test import Client, TestCase
from django.utils import timezone
from django.contrib.admin.sites import AdminSite

from .models import Ballot, Question, Choice


class BallotModelTests(TestCase):
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

    def test_ballot_model_str(self):
        """
        Making sure the return str for ballot title is the same str given
        """
        ballot = Ballot.objects.create(
            ballot_title="Test Case Ballot",
            ballot_description="Making sure the return str is the same",
            pub_date=timezone.now(),
            due_date=timezone.now() + datetime.timedelta(days=30)
        )
        self.assertEqual(str(ballot), "Test Case Ballot")

    """
    makes sure the due date of the ballot is after the publish.
    Don't want a ballot to be past due as soon as it is created.
    Fixed by clean function in models.py
    """


class QuestionModelTests(TestCase):
    def test_question_model_str(self):
        """
        Making sure the return str for question text is the same str given
        """
        ballot = Ballot.objects.create(
            ballot_title="Test Case Ballot",
            ballot_description="Making sure the question return str is the same",
            district="All",
            pub_date=timezone.now(),
            due_date=timezone.now() + datetime.timedelta(days=30)
        )
        question = Question.objects.create(
            ballot=ballot,
            question_text="Make sure the return str is same"
        )
        self.assertEqual(str(question), "Make sure the return str is same")


class ChoiceModelTests(TestCase):
    def test_choice_model_str(self):
        """
        Making sure the return str for choice text is the same str given
        """
        ballot = Ballot.objects.create(
            ballot_title="Test Case Ballot",
            ballot_description="Making sure the question return str is the same",
            district="All",
            pub_date=timezone.now(),
            due_date=timezone.now() + datetime.timedelta(days=30)
        )
        question = Question.objects.create(
            ballot=ballot,
            question_text="Make sure the return str is same"
        )
        choice1 = Choice.objects.create(
            question=question,
            choice_text="True",
        )
        choice2 = Choice.objects.create(
            question=question,
            choice_text="False",
        )
        self.assertEqual(str(choice1), "True")
        self.assertEqual(str(choice2), "False")

    def test_choice_vote_count(self):
        """
        Making sure the read only votes field can still increment when someone votes
        """
        ballot = Ballot.objects.create(
            ballot_title="Test Case Ballot",
            ballot_description="Making sure the question return str is the same",
            district="All",
            pub_date=timezone.now(),
            due_date=timezone.now() + datetime.timedelta(days=30)
        )
        question = Question.objects.create(
            ballot=ballot,
            question_text="Make sure the return str is same"
        )
        choice = Choice.objects.create(
            question=question,
            choice_text="True",
            votes=0
        )
        self.assertEqual(choice.votes, 0)
        choice.votes += 1
        self.assertEqual(choice.votes, 1)
