from django.shortcuts import render


def order_list(request):
    return render(request, "pages/orders.html")


def order_detail(request, order_id):
    return render(request, "pages/order_detail.html", {"order_id": order_id})
