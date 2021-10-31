from django.db import models

# Create your models here.

class Ballot(models.Model):
    ballot_title = models.TextField()
    questions = models.TextField()