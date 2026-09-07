from django.urls import path

from . import views_teacher as views

app_name = "teacher"

urlpatterns = [
    path("", views.groups, name="groups"),
    path("guruh/yangi/", views.group_create, name="group_create"),
    path("guruh/<int:pk>/", views.group_detail, name="group_detail"),
    path("guruh/<int:pk>/analitika/", views.analytics, name="analytics"),
    path("guruh/<int:pk>/elon/", views.announce, name="announce"),
    path("guruh/<int:pk>/talaba/<int:user_id>/", views.student_card, name="student_card"),
]
