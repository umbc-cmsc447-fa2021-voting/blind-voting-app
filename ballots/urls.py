from django.urls import path
from .views import AddBallotView
from . import views

app_name = 'ballots'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:ballot_id>/', views.detail, name='detail'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('add/', AddBallotView.as_view(), name='add'),
]