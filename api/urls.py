from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("robots/", views.robots, name="robots"),
    path("robots/<int:robot_id>/", views.robot_detail, name="robot_detail"),
    path("brands/", views.brands, name="brands"),
    path("categories/", views.categories, name="categories"),
]
