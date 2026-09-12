from django.urls import path

from . import views

app_name = "progress"

urlpatterns = [
    path("", views.monitoring, name="monitoring"),
    path("kuzatuv/", views.observation, name="observation"),
    path("hisobot/pdf/", views.report_pdf, name="report_pdf"),
    path("kunlik/bajarildi/", views.daily_done, name="daily_done"),
    path("oqituvchi/<int:user_id>/", views.student_monitoring, name="student"),
]
