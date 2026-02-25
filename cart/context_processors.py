from .models import Cart

def cart_info(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            count = sum(item.quantity for item in cart.items.all())
        else:
            count = 0
    else:
        session_cart = request.session.get("cart", {})
        items = session_cart.get("items", {})
        count = 0
        for qty in items.values():
            try:
                count += int(qty)
            except (TypeError, ValueError):
                continue

    return {
        "cart_items_count": count
    }
