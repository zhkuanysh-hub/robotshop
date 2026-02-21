# shipping/views.py
from django.http import HttpResponse

def index(request):
    return HttpResponse("Shipping works")