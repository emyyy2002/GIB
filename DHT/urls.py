from django.urls import path
from . import views, api

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("latest/", views.latest_json, name="latest_json"),

    path("api/", api.Dlist, name="json"),  # Function - no .as_view()
    path("api/post", api.Dhtviews.as_view(), name="json_post"),  # Class - with .as_view()

    path("temperature/history/", views.temperature_history, name="temperature_history"),
    path(
        "temperature/history/csv/",
        views.temperature_history_csv,
        name="temperature_history_csv",
    ),

    path("humidity/history/", views.humidity_history, name="humidity_history"),
    path(
        "humidity/history/csv/",
        views.humidity_history_csv,
        name="humidity_history_csv",
    ),
]