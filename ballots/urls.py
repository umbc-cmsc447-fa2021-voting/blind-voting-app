from django.urls import path
from .views import AddBallotView, BallotEditView, BallotAdminView, PublishedBallotsView, AddQuestionView, AddChoiceView
from .views import BallotDetailView, PastBallotsView
from . import views

app_name = 'ballots'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:ballot_id>/', views.detail, name='detail'),
    path('<int:ballot_id>/<int:question_id>/question/', views.detail_q, name='detail-q'),
    path('<int:ballot_id>/<int:question_id>/vote/', views.vote, name='vote'),
    path('<int:ballot_id>/results/', views.results, name='results'),
    path('ballot-admin', BallotAdminView.as_view(), name='ballot-admin'),
    path('ballot-admin/published', PublishedBallotsView.as_view(), name='published'),
    path('ballot-admin/past', PastBallotsView.as_view(), name='past'),
    path('add/', AddBallotView.as_view(), name='add'),
    path('<int:pk>/edit', BallotEditView.as_view(), name='edit'),
    path('<int:pk>/detail', BallotDetailView.as_view(), name='ballot-detail'),
    path('<int:pk>/questions/', AddQuestionView.as_view(), name='questions'),
    path('<int:pk>/choices/', AddChoiceView.as_view(), name='choices'),
]