from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Robot
from .models import Cart, CartItem


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user, defaults={"is_active": True})
    if not cart.is_active:
        cart.is_active = True
        cart.save(update_fields=["is_active"])
    return cart


@login_required
def cart_detail(request):
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related("robot").all()

    total = sum((item.robot.price * item.quantity for item in items), Decimal("0.00"))

    return render(request, "cart/cart_detail.html", {
        "cart": cart,
        "items": items,
        "total": total,
    })


@login_required
@require_POST
@transaction.atomic
def add_to_cart(request, robot_id):
    cart = _get_or_create_cart(request.user)
    robot = get_object_or_404(Robot, id=robot_id, is_active=True)

    item, created = CartItem.objects.select_for_update().get_or_create(
        cart=cart,
        robot=robot,
        defaults={"quantity": 1},
    )

    if not created:
        item.quantity += 1
        item.save(update_fields=["quantity"])

    return redirect("cart:index")


@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart = _get_or_create_cart(request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect("cart:index")


@login_required
@require_POST
def update_cart_item(request, item_id):
    cart = _get_or_create_cart(request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        qty = int(request.POST.get("quantity", "1"))
    except ValueError:
        qty = 1

    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save(update_fields=["quantity"])

    return redirect("cart:index")