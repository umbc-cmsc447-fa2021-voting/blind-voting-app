from django.contrib.auth.views import redirect_to_login
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import UpdateView, CreateView, ListView, FormView
from django.views.generic.detail import SingleObjectMixin, DetailView
from .forms import AddBallotForm, BallotQuestionFormset, QuestionChoiceFormset

# Create your views here.

from ballots.models import Ballot, Question, Choice

def index(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    today = timezone.now()
    ballot_list = Ballot.objects.filter(pub_date__lte=today).filter(district__iexact=request.user.profile.district).order_by('due_date')
    context = {"ballot_list": ballot_list, "today": today}
    return render(request, 'ballots/index.html', context=context)

def detail(request, ballot_id):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    try:
        ballot = Ballot.objects.get(pk=ballot_id)
        question_list = Question.objects.filter(ballot=ballot_id)
        context = {'ballot': ballot, 'question_list': question_list}
    except Ballot.DoesNotExist:
        raise Http404("Ballot does not exist")
    return render(request, 'ballots/detail.html', context=context)

def vote(request, question_id):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
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

class UserAccessMixin(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('/users/login/')
        if not self.has_permission():
            return redirect(reverse('ballots:index'))
        return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)

class BallotAdminView(UserAccessMixin, ListView):
    raise_exception = False
    permission_required = 'ballot.change_ballot'

    model = Ballot
    template_name = "ballot_admin.html"
    context_object_name = "ballots"

    def get_queryset(self, *args, **kwargs):
        return Ballot.objects.filter(pub_date__gte=timezone.now())

class PublishedBallotsView(UserAccessMixin, ListView):
    permission_required = 'ballot.change_ballot'

    model = Ballot
    template_name = "published-ballots.html"
    context_object_name = "ballots"

    def get_queryset(self, *args, **kwargs):
        return Ballot.objects.filter(pub_date__lte=timezone.now()).filter(due_date__gte=timezone.now())

class PastBallotsView(UserAccessMixin, ListView):
    permission_required = 'ballot.change_ballot'

    model = Ballot
    template_name = "past-ballots.html"
    context_object_name = "ballots"

    def get_queryset(self, *args, **kwargs):
        return Ballot.objects.filter(due_date__lte=timezone.now())

class AddBallotView(UserAccessMixin, CreateView):
    permission_required = 'ballot.change_ballot'

    template_name = 'add.html'
    form_class = AddBallotForm
    success_url = '/ballot-admin'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class BallotEditView(UserAccessMixin, UpdateView):
    permission_required = 'ballot.change_ballot'

    model = Ballot
    form_class = AddBallotForm
    template_name = 'ballotedit.html'
    success_url = '/ballot-admin'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if(self.get_object().pub_date <= timezone.now()):
            return redirect('/ballot-admin')
        return super().get(request, *args, **kwargs)

class AddQuestionView(UserAccessMixin, SingleObjectMixin, FormView):
    permission_required = 'ballot.change_ballot'

    model = Question
    template_name = 'addquestion.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Ballot.objects.all())
        if (self.object.pub_date <= timezone.now()):
            return redirect('/ballot-admin')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Ballot.objects.all())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return BallotQuestionFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Changes were saved.'
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('ballots:edit', kwargs={'pk': self.object.pk})


class AddChoiceView(UserAccessMixin, SingleObjectMixin, FormView):
    permission_required = 'ballot.change_ballot'

    model = Choice
    template_name = 'addchoice.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Question.objects.all())
        if (self.object.ballot.pub_date <= timezone.now()):
            return redirect('/ballot-admin')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Question.objects.all())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return QuestionChoiceFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Changes were saved.'
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('ballots:questions', kwargs={'pk': self.object.ballot.pk})

class BallotDetailView(DetailView):
    model = Ballot
    template_name = 'ballot-detail.html'
    context_object_name = 'ballot'


