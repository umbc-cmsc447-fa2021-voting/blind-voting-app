from django.db import models
from datetime import datetime

# Create your models here.

class Ballot(models.Model):
    ballot_title = models.TextField(max_length=200)
    pub_date = models.DateTimeField('date published', default=datetime.now, blank=True)

    def __str__(self):
        return self.ballot_title

class Question(models.Model):
    ballot1 = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    question_text = models.TextField(max_length=200)

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    ballot2 = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text