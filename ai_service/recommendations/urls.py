from django.urls import path
from .views import (
    ChatView,
    ETLView,
    HealthView,
    RecommendView,
    SearchView,
    TrackEventView,
    UserHistoryView,
    get_recommendation,
)

urlpatterns = [
    path("events/", TrackEventView.as_view()),
    path("recommendations/", RecommendView.as_view()),
    path("search/", SearchView.as_view()),
    path("chat/", ChatView.as_view()),
    path("health/", HealthView.as_view()),
    path("etl/", ETLView.as_view()),
    path("history/", UserHistoryView.as_view()),
    path("recommend/", get_recommendation),
]
