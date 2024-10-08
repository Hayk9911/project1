from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    path('', views.index, name='index'),
    path("<int:question_id>/", views.detail, name="detail"),
    # ex: /polls/5/results/
    path("<int:question_id>/results/", views.results, name="results"),
    # ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("register/", views.register, name="register"),
    path("login/" , views._login, name="login"),
    path("logout", views.log_out, name="logout"),
    path("question/", views.question, name="question"),
    path("<int:question_id>/question/edit/", views.question_edit, name="question_edit")
]

