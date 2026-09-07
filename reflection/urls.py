from django.urls import path

from . import views

app_name = "reflection"

urlpatterns = [
    path("", views.journal, name="journal"),
    path("yangi/", views.create_free, name="create_free"),
    path("ish/<int:submission_id>/", views.create_for_submission, name="create_for_submission"),
    path("<int:pk>/", views.detail, name="detail"),
]
