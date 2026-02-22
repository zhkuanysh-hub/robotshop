from .models import Cart

def cart_info(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            count = sum(item.quantity for item in cart.items.all())
        else:
            count = 0
    else:
        count = 0

    return {
        "cart_items_count": count
    }