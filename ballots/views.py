from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

# Create your views here.

from ballots.models import Ballot, Question, Choice

def index(request):
    ballot_list = Ballot.objects.order_by('-pub_date')
    context = {"ballot_list": ballot_list}
    return render(request, 'ballots/index.html', context=context)

def detail(request, ballot_id):
    try:
        ballot = Ballot.objects.get(pk=ballot_id)
        question_list = Question.objects.filter(ballot=ballot_id)
        context = {'ballot': ballot, 'question_list': question_list}
    except Ballot.DoesNotExist:
        raise Http404("Ballot does not exist")
    return render(request, 'Ballots/detail.html', context=context)

def vote(request, question_id):
    # print(request.POST['choice'])
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'ballots/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('ballots:index'))