from django.urls import path
from . import views

# app_name = 'articles'

urlpatterns = [
    # ex: /polls/
    path('', views.home, name='home'),
    # ex: /polls/5/
    path('article/<str:article_id>/', views.article, name='detail'),
    # # ex: /polls/5/results/
    path('vote/', views.vote, name='vote'),

    # path('<int:question_id>/results/', views.results, name='results'),
    # # ex: /polls/5/vote/
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]