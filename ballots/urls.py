from django.urls import path
from .views import AddBallotView, BallotEditView, BallotAdminView, AddQuestionView
from . import views

app_name = 'ballots'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:ballot_id>/', views.detail, name='detail'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('ballot-admin', BallotAdminView.as_view(), name='ballot-admin'),
    path('add/', AddBallotView.as_view(), name='add'),
    path('<slug:slug>/', BallotEditView.as_view(), name='edit'),
    path('<slug:slug>/questions/', AddQuestionView.as_view(), name='questions'),
]