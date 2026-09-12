from django.urls import path

from . import builders, views_crud
from . import views_manage as views

app_name = "manage"

urlpatterns = [
    path("", views.students, name="students"),
    path("analitika/", views.analytics, name="analytics"),
    path("elon/", views.announce, name="announce"),
    path("oqituvchi/<int:user_id>/", views.student_card, name="student_card"),
    path("menyu/", views.menu, name="menu"),
    path("menyu/tartib/", views.menu_reorder, name="menu_reorder"),
    path("menyu/nom/", views.menu_rename, name="menu_rename"),
    path("menyu/blok/yangi/", views.menu_group_add, name="menu_group_add"),
    path("menyu/blok/<slug:group>/ochirish/", views.menu_group_delete, name="menu_group_delete"),
    path("menyu/band/saqlash/", views.menu_item_save, name="menu_item_save"),
    path("menyu/band/<str:key>/ochirish/", views.menu_item_delete, name="menu_item_delete"),
    path("menyu/<slug:group>/standart/", views.menu_reset, name="menu_reset"),
    # Sodda quruvchilar: test, rubrika, nishon, dars, fan, mavzu.
    path("yaratish/<slug:kind>/", builders.builder, name="builder_new"),
    path("yaratish/<slug:kind>/<int:pk>/", builders.builder, name="builder_edit"),
    # Universal CRUD (accounts.crud reyestri).
    path("malumotlar/", views_crud.crud_index, name="crud_index"),
    path("malumotlar/<slug:key>/", views_crud.crud_list, name="crud_list"),
    path("malumotlar/<slug:key>/yangi/", views_crud.crud_create, name="crud_create"),
    path("malumotlar/<slug:key>/tartib/", views_crud.crud_reorder, name="crud_reorder"),
    path("malumotlar/<slug:key>/<int:pk>/", views_crud.crud_edit, name="crud_edit"),
    path("malumotlar/<slug:key>/<int:pk>/ochirish/", views_crud.crud_delete, name="crud_delete"),
    path("malumotlar/<slug:key>/<int:pk>/tiklash/", views_crud.crud_restore, name="crud_restore"),
    path("malumotlar/<slug:key>/<int:pk>/butunlay/", views_crud.crud_purge, name="crud_purge"),
]
