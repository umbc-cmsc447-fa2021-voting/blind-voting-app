import datetime
import uuid

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.urls import reverse

# Create your models here.

class Ballot(models.Model):
    ballot_title = models.TextField(max_length=200, default="")
    ballot_description = models.TextField(max_length=200, default="", blank=True)
    pub_date = models.DateTimeField('date published', default=timezone.now())
    due_date = models.DateTimeField('due date', default=timezone.now()+datetime.timedelta(days=30))
    district = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(max_length=200, default=uuid.uuid1, editable=False)

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        return self.ballot_title

    def get_absolute_url(self):
        return reverse('ballots:edit', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(uuid.uuid1)
        return super().save(*args, **kwargs)

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