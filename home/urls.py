from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("loyiha-haqida/", views.about, name="about"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("kabinet/", views.cabinet, name="cabinet"),
    path("bolim/<slug:slug>/", views.upcoming, name="upcoming"),
]
