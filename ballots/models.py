import datetime
from django.db import models
from django.utils import timezone

# Create your models here.

class Ballot(models.Model):
    ballot_title = models.TextField(max_length=200, blank=True)
    ballot_description = models.TextField(max_length=200, blank=True)
    pub_date = models.DateTimeField('date published', blank=True)
    due_date = models.DateTimeField('due date', blank=True)

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        return self.ballot_title

class Question(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    question_text = models.TextField(max_length=200)

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text