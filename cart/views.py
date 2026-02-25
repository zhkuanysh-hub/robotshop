from decimal import Decimal
from types import SimpleNamespace

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Robot
from .models import Cart, CartItem

SESSION_CART_KEY = "cart"


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user, defaults={"is_active": True})
    if not cart.is_active:
        cart.is_active = True
        cart.save(update_fields=["is_active"])
    return cart


def _session_cart_items(request):
    data = request.session.get(SESSION_CART_KEY, {})
    raw_items = data.get("items", {})

    ids = []
    for rid, qty in raw_items.items():
        try:
            rid_int = int(rid)
            qty_int = int(qty)
        except (TypeError, ValueError):
            continue
        if qty_int > 0:
            ids.append(rid_int)

    robots = Robot.objects.filter(id__in=ids).select_related("brand", "category")
    robots_map = {r.id: r for r in robots}

    items = []
    for rid in ids:
        robot = robots_map.get(rid)
        if not robot:
            continue
        qty = int(raw_items.get(str(rid), 0))
        if qty < 1:
            continue
        # template compatibility with CartItem-like fields
        items.append(SimpleNamespace(id=rid, robot=robot, quantity=qty))

    return items


def cart_get(request):
    if request.user.is_authenticated:
        cart = _get_or_create_cart(request.user)
        items = list(cart.items.select_related("robot", "robot__brand", "robot__category"))
        return {"type": "db", "cart": cart, "items": items}

    items = _session_cart_items(request)
    return {"type": "session", "cart": None, "items": items}


def cart_detail(request):
    data = cart_get(request)
    items = data["items"]
    total = sum((item.robot.price * item.quantity for item in items), Decimal("0.00"))

    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart": data["cart"],
            "items": items,
            "total": total,
        },
    )


@require_POST
@transaction.atomic
def add_to_cart(request, robot_id):
    robot = get_object_or_404(Robot, id=robot_id, is_active=True)

    if request.user.is_authenticated:
        cart = _get_or_create_cart(request.user)
        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            robot=robot,
            defaults={"quantity": 1},
        )

        if not created:
            item.quantity += 1
            item.save(update_fields=["quantity"])
    else:
        session_cart = request.session.get(SESSION_CART_KEY, {"items": {}})
        items = session_cart.setdefault("items", {})
        key = str(robot.id)
        items[key] = int(items.get(key, 0)) + 1
        request.session[SESSION_CART_KEY] = session_cart
        request.session.modified = True

    return redirect("cart:index")


@require_POST
def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        cart = _get_or_create_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
    else:
        session_cart = request.session.get(SESSION_CART_KEY, {"items": {}})
        items = session_cart.setdefault("items", {})
        items.pop(str(item_id), None)
        request.session[SESSION_CART_KEY] = session_cart
        request.session.modified = True

    return redirect("cart:index")


@require_POST
def update_cart_item(request, item_id):
    try:
        qty = int(request.POST.get("quantity", "1"))
    except ValueError:
        qty = 1

    if request.user.is_authenticated:
        cart = _get_or_create_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        if qty < 1:
            item.delete()
        else:
            item.quantity = qty
            item.save(update_fields=["quantity"])
    else:
        session_cart = request.session.get(SESSION_CART_KEY, {"items": {}})
        items = session_cart.setdefault("items", {})
        key = str(item_id)
        if qty < 1:
            items.pop(key, None)
        else:
            items[key] = qty
        request.session[SESSION_CART_KEY] = session_cart
        request.session.modified = True

    return redirect("cart:index")
