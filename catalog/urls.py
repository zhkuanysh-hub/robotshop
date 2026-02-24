from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.robot_list, name="list"),
    path("<slug:slug>/", views.robot_detail, name="detail"),
]

