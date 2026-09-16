from django.urls import path

from . import views

app_name = "socratic"

urlpatterns = [
    path("", views.chat, name="chat"),
    path("boshlash/", views.start, name="start"),
    path("xabar/", views.message, name="message"),
    path("saqlash/", views.save, name="save"),
]
