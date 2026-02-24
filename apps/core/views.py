from django.shortcuts import render

def home(request):
    return render(request, "pages/home.html")


def about(request):
    return render(request, "pages/about.html")

def login_page(request):
    return render(request, "pages/login_np.html")