from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("", views.index, name="index"),
    path("dars/<int:pk>/test/", views.lesson_quiz, name="lesson_quiz"),
    path("bolim/<slug:slug>/", views.section_detail, name="section"),
    path("<slug:section_slug>/<slug:topic_slug>/", views.topic_detail, name="topic"),
    path("<slug:section_slug>/<slug:topic_slug>/<slug:lesson_slug>/", views.lesson_detail, name="lesson"),
]
