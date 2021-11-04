from django import forms
from .models import Ballot, Question, Choice
from django.forms.models import inlineformset_factory

class AddBallotForm(forms.ModelForm):
    class Meta:
        model = Ballot
        fields = {'ballot_title', 'ballot_description', 'pub_date', 'due_date', 'district'}

        widgets = {
            'ballot_title': forms.TextInput(attrs={'class': 'form-control'}),
            'ballot_description': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
        }

        field_order = ['ballot_title', 'ballot_description', 'pub_date', 'due_date', 'district']

BallotQuestionFormset = inlineformset_factory(Ballot, Question, fields=('question_text',))