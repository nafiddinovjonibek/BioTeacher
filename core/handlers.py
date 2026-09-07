"""Xato sahifalari (NFR-12 — ruxsat rad etilganda tushunarli xabar)."""

from django.shortcuts import render


def bad_request(request, exception=None):
    return render(request, "errors/error.html",
                  {"code": 400, "title": "So'rov noto'g'ri"}, status=400)


def permission_denied(request, exception=None):
    return render(request, "errors/error.html", {
        "code": 403,
        "title": "Ruxsat yo'q",
        "message": str(exception) or "Bu sahifani ko'rish huquqingiz yo'q.",
    }, status=403)


def page_not_found(request, exception=None):
    return render(request, "errors/error.html",
                  {"code": 404, "title": "Sahifa topilmadi"}, status=404)


def server_error(request):
    return render(request, "errors/error.html",
                  {"code": 500, "title": "Serverda xatolik"}, status=500)
