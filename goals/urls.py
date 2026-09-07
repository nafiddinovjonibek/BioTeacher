from django.urls import path

from . import views

app_name = "goals"

urlpatterns = [
    path("", views.goal_list, name="list"),
    path("yangi/", views.goal_create, name="create"),
    path("<int:pk>/", views.goal_detail, name="detail"),
    path("<int:pk>/tahrir/", views.goal_edit, name="edit"),
    path("<int:pk>/yakunlash/", views.goal_close, name="close"),
    path("<int:pk>/refleksiya/", views.goal_reflect, name="reflect"),
    path("<int:pk>/mentor-izohi/", views.goal_review, name="review"),
    path("vazifa/<int:pk>/belgilash/", views.toggle_task, name="toggle_task"),
]
