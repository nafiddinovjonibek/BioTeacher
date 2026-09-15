"""BioTeacher URL xaritasi (TZ 7.1)."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "BioTeacher — boshqaruv paneli"
admin.site.site_title = "BioTeacher"
admin.site.index_title = "Platforma boshqaruvi"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("hisob/", include("accounts.urls")),
    path("diagnostika/", include("diagnostics.urls")),
    path("maqsadlar/", include("goals.urls")),
    path("biobilim/", include("content.urls")),
    path("topshiriqlar/", include("assignments.urls")),
    path("amaliyot/", include("development.urls")),
    path("refleksiya/", include("reflection.urls")),
    path("rivojlanish/", include("progress.urls")),
    path("yutuqlar/", include("gamification.urls")),
    path("tadqiqot/", include("research.urls")),
    path("bildirishnomalar/", include("notifications.urls")),
    path("boshqaruv/", include("accounts.urls_manage")),
    path("", include("home.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "core.handlers.bad_request"
handler403 = "core.handlers.permission_denied"
handler404 = "core.handlers.page_not_found"
handler500 = "core.handlers.server_error"
