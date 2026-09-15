from django.contrib import admin

from .models import PlotResource, Simulation


@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "order", "is_active")
    list_filter = ("section", "is_active")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(PlotResource)
class PlotResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "season", "grade", "order", "is_active")
    list_filter = ("kind", "season", "is_active")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
