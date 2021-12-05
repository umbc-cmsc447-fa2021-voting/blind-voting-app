import datetime
import uuid

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


# Create your models here.
from django_cryptography.fields import encrypt


def now_plus_7():
    return timezone.now() + datetime.timedelta(days=7)

def now_plus_30():
    return timezone.now() + datetime.timedelta(days=30)


class Ballot(models.Model):
    ballot_title = models.TextField(max_length=200, default="")
    ballot_description = models.TextField(max_length=200, default="", blank=True)
    pub_date = models.DateTimeField('date published', default=now_plus_7)
    due_date = models.DateTimeField('due date', default=now_plus_30)
    district = models.CharField(max_length=50, blank=True)

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    # Checks if the due date is after publish date
    def clean(self):
        if self.due_date < self.pub_date:
            raise ValidationError(_('Due Date should be further in the future than Publish Date.'), code='invalid')

    def __str__(self):
        return self.ballot_title

    def get_absolute_url(self):
        return reverse('ballots:edit', kwargs={'slug': self.slug})


class Question(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    question_text = models.TextField(max_length=200)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return self.choice_text

class CastBallot(models.Model):
    assoc_ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)

class CastVote(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    ballot = models.ForeignKey(CastBallot, on_delete=models.CASCADE)

class VoteRecord(models.Model):
    assoc_ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    voter_signature = models.CharField(max_length=50)