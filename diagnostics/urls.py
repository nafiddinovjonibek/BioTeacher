from django.urls import path

from . import views

app_name = "diagnostics"

urlpatterns = [
    path("", views.index, name="index"),
    path("boshlash/<slug:slug>/", views.start, name="start"),
    path("urinish/<int:attempt_id>/", views.take, name="take"),
    path("urinish/<int:attempt_id>/javob/", views.answer, name="answer"),
    path("urinish/<int:attempt_id>/yakunlash/", views.finish, name="finish"),
    path("urinish/<int:attempt_id>/natija/", views.result, name="result"),
]
