from django.urls import path

from . import views

app_name = "development"

urlpatterns = [
    path("3d-simulyatsiyalar/", views.simulations, name="simulations"),
    path("3d-simulyatsiyalar/<slug:slug>/", views.simulation_detail, name="simulation"),
    path("tajriba-uchastkasi/", views.plot, name="plot"),
    path("tajriba-uchastkasi/<slug:slug>/", views.plot_detail, name="plot_resource"),
]
