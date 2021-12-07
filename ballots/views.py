import datetime

from django.contrib.auth.views import redirect_to_login
from django.core.signing import Signer
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_list_or_404, render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils import timezone
from django.views.generic import UpdateView, CreateView, ListView, FormView
from django.views.generic.detail import SingleObjectMixin, DetailView
from .forms import AddBallotForm, BallotQuestionFormset, QuestionChoiceFormset

# Create your views here.

from ballots.models import Ballot, Question, Choice, CastVote, VoteRecord, CastBallot


def index(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    signer = Signer()
    sign = signer.sign(request.user.profile.sign)
    sign = sign[51:]
    today = timezone.now()
    vote_records = VoteRecord.objects.filter(voter_signature__exact=sign)
    finished_ballot_ids = []
    for record in vote_records:
        finished_ballot_ids.append(record.assoc_ballot.id)
    ballot_list = Ballot.objects.filter(pub_date__lte=today).filter(district__iexact=request.user.profile.district)\
        .exclude(id__in=finished_ballot_ids).order_by('due_date')
    finished_ballots = Ballot.objects.filter(pub_date__lte=today).filter(district__iexact=request.user.profile.district)\
        .filter(id__in=finished_ballot_ids).order_by('due_date')
    context = {"ballot_list": ballot_list, "finished_ballots": finished_ballots, "today": today}
    return render(request, 'ballots/index.html', context=context)


def detail(request, ballot_id):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    try:
        ballot = Ballot.objects.get(pk=ballot_id)
        question_list = Question.objects.filter(ballot=ballot_id)
        b_id = ballot_id
        context = {'ballot': ballot, 'question_list': question_list, 'current_b_id': b_id}
    except Ballot.DoesNotExist:
        raise Http404("Ballot does not exist")
    signer = Signer()
    sign = signer.sign(request.user.profile.sign)
    sign = sign[51:]
    if ballot.due_date > timezone.now() and ballot.pub_date < timezone.now()\
            and ballot.district.lower() == request.user.profile.district.lower() and not\
            VoteRecord.objects.filter(voter_signature=sign).filter(assoc_ballot=ballot).exists():
        return render(request, 'ballots/detail.html', context=context)
    else:
        raise PermissionDenied


def detail_q(request, ballot_id, question_id):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    try:

        ballot = Ballot.objects.get(pk=ballot_id)
        current_ballot = ballot_id
        question = get_object_or_404(Question, pk=question_id)
        context = {'current_b_id': current_ballot, 'question': question}
    except Ballot.DoesNotExist:
        raise Http404("Ballot does not exist")
    if ballot.pub_date > timezone.now() or ballot.due_date < timezone.now() \
            or ballot.district.lower() != request.user.profile.district.lower():
        return redirect(reverse('ballots:index'))
    return render(request, 'ballots/detail.html', context=context)


def results(request, ballot_id):
    try:
        ballot = Ballot.objects.get(pk=ballot_id)
        question_list = Question.objects.filter(ballot=ballot_id)
        context = {'ballot': ballot, 'question_list': question_list}
    except Ballot.DoesNotExist:
        raise Http404("Ballot does not exist")
    if ballot.due_date > timezone.now():
        return redirect(reverse('ballots:index'))
    return render(request, 'ballots/vote.html', context=context)



def vote(request, ballot_id):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    # print(request.POST['choice'])
    ballot = get_object_or_404(Ballot, pk=ballot_id)
    questions = get_list_or_404(Question, ballot=ballot)
    signer = Signer()
    sign = signer.sign(request.user.profile.sign)
    sign = sign[51:]
    if ballot.pub_date > timezone.now() or ballot.due_date < timezone.now() \
            or ballot.district.lower() != request.user.profile.district.lower()\
            or VoteRecord.objects.filter(voter_signature=sign).filter(assoc_ballot=ballot).exists():
        return redirect(reverse('ballots:index'))
    if questions:
        selected_choices = []
        for question in questions:
            if request.POST.get(question.question_text):
                selected_choices.append(question.choice_set.get(pk=request.POST[question.question_text]))
        if len(selected_choices) > 0:
            signer = Signer()
            sign = signer.sign(request.user.profile.sign)
            sign = sign[51:]
            new_record = VoteRecord.objects.create(assoc_ballot=ballot, voter_signature=sign)
            new_record.save()
            new_ballot = CastBallot.objects.create(assoc_ballot=ballot)
            new_ballot.save()
            for choice in selected_choices:
                new_vote = CastVote.objects.create(choice=choice, ballot=new_ballot)
                new_vote.save()
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
        return Ballot.objects.filter(due_date__lte=timezone.now()).filter(due_date__gte=timezone.now() - datetime.timedelta(days=365.25))


class ArchivedBallotsView(UserAccessMixin, ListView):
    permission_required = "ballot.change_ballot"

    model = Ballot
    template_name = "archived-ballots.html"
    context_object_name = "ballots"

    def get_queryset(self, *args, **kwargs):
        return Ballot.objects.filter(due_date__lte=timezone.now() - datetime.timedelta(days=365.24))

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

    def get_context_data(self, **kwargs):
        context = super(BallotDetailView, self).get_context_data(**kwargs)
        context['today'] = timezone.now()
        return context


