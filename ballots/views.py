from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

from ballots.models import Ballot

def index(request):
    ballot_list = Ballot.objects.order_by('-pub_date')
    context = {"ballot_list": ballot_list}
    return render(request, 'ballots/index.html', context=context)