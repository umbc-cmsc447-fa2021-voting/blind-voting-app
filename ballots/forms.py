from django.utils import timezone
import datetime
from django import forms
from django.core.exceptions import ValidationError

from .models import Ballot, Question, Choice
from django.forms.models import inlineformset_factory

def now_plus_7():
    return timezone.now() + datetime.timedelta(days=7)

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

    def clean_pub_date(self):
        data = self.cleaned_data.get('pub_date')
        if data <= timezone.now():
            raise forms.ValidationError("Invalid publication date - publication must be in the future")
        return data

    def clean(self):
        cleaned_data = super().clean()
        pub = cleaned_data.get('pub_date')
        due = cleaned_data.get('due_date')

        if pub and due:
            if pub >= due:
                raise ValidationError("Invalid publication date - publication must be before due date")


BallotQuestionFormset = inlineformset_factory(Ballot, Question, fields=('question_text',))


QuestionChoiceFormset = inlineformset_factory(Question, Choice, fields=('choice_text',))
