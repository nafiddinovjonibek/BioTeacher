from django.urls import path

from . import views

app_name = "assignments"

urlpatterns = [
    path("modul/<str:module>/", views.module_list, name="module"),
    path("galereya/", views.gallery, name="gallery"),
    path("kompetensiya/", views.competency, name="competency"),
    path("navbat/", views.queue, name="queue"),
    path("ish/<int:pk>/", views.submission_detail, name="submission"),
    path("ish/<int:pk>/baholash/", views.grade, name="grade"),
    path("ish/<int:pk>/ozini-baholash/", views.self_assess, name="self_assess"),
    path("ish/<int:pk>/refleksiya/", views.reflect_redirect, name="reflect"),
    path("ish/<int:pk>/pdf/", views.submission_pdf, name="submission_pdf"),
    path("ish/<int:pk>/qaytarish/", views.reopen, name="reopen"),
    path("<slug:slug>/", views.assignment_detail, name="detail"),
]
