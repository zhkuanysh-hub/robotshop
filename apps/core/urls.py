from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("stats/", views.stats_brands, name="stats"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("delivery/", views.delivery, name="delivery"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("faq/", views.faq, name="faq"),
    path("blog/", views.blog, name="blog"),
    path("login-page/", views.login_page, name="login_page"),
]
