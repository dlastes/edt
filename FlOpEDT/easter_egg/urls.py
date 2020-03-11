from django.urls import path
from . import views

app_name = "easter_egg"

urlpatterns = [
    path('', views.start_game, name="start_game"),
    path('fetch_leaderboard', views.fetch_leaderboard, name="fetch_leaderboard"),
    path('set_score/<int:score>', views.set_score, name="set_score"),
    path('set_score', views.set_score, name="set_score"),
]