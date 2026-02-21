# cart/views.py
from django.http import HttpResponse

def index(request):
    return HttpResponse("Cart works")