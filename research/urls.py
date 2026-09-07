from django.urls import path

from . import views

app_name = "research"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("eksport/", views.export, name="export"),
    path("statistika/", views.statistics, name="statistics"),
    path("statistika/yangilash/", views.refresh_stats, name="refresh_stats"),
    path("guruh/<int:group_id>/bolinma/", views.set_arm, name="set_arm"),
]
