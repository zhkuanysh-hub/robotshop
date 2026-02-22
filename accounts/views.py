from django.shortcuts import render


def login_view(request):
    return render(request, "pages/login.html")


def register_view(request):
    return render(request, "pages/register.html")


def profile_view(request):
    return render(request, "pages/profile.html")



from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})