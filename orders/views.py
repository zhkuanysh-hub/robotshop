from decimal import Decimal
from decimal import InvalidOperation
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Cart, CartItem
from catalog.models import Robot
from accounts.models import Address

from .models import Order, OrderItem, OrderStatusHistory

logger = logging.getLogger("robotshop")


@login_required
def order_list(request):
    orders = request.user.orders.all()
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    try:
        order = get_object_or_404(
            Order.objects.prefetch_related("items__robot"),
            pk=pk,
            user=request.user,
        )
    except (InvalidOperation, DatabaseError):
        logger.error(
            "Failed to load order detail due to invalid decimal data. order_id=%s user_id=%s",
            pk,
            request.user.id,
            exc_info=True,
        )
        messages.error(
            request,
            "Не удалось открыть заказ из-за некорректных данных суммы. Попробуйте позже.",
        )
        return redirect("orders:list")
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
@transaction.atomic
def checkout(request):
    if request.method != "POST":
        return redirect("cart:index")

    cart = get_object_or_404(Cart, user=request.user, is_active=True)
    cart_items = CartItem.objects.select_for_update().select_related("robot").filter(cart=cart)

    if not cart_items.exists():
        messages.error(request, "Корзина пуста.")
        return redirect("cart:index")

    # ⚠ ВАЖНО: у тебя Order требует address
    # Берём первый адрес пользователя
    address = Address.objects.filter(user=request.user).first()

    if not address:
        messages.error(request, "Добавьте адрес перед оформлением заказа.")
        return redirect("cart:index")

    total = Decimal("0.00")

    # Проверяем склад
    for item in cart_items:
        robot = item.robot

        if robot.stock < item.quantity:
            messages.error(
                request,
                f"Недостаточно товара '{robot.name}'. В наличии: {robot.stock}"
            )
            return redirect("cart:index")

        unit_price = robot.price or Decimal("0.00")
        total += unit_price * item.quantity

    if total < Decimal("0.00") or total > Decimal("99999999.99"):
        logger.error(
            "Order total out of bounds. user_id=%s total=%s",
            request.user.id,
            total,
        )
        messages.error(
            request,
            "Сумма заказа превышает допустимый предел. Измените количество товаров.",
        )
        return redirect("cart:index")

    # Создаём заказ
    order = Order.objects.create(
        user=request.user,
        address=address,
        total_amount=total,
        status=Order.Status.NEW,
    )

    # История статуса
    OrderStatusHistory.objects.create(
        order=order,
        status=Order.Status.NEW,
        comment="Заказ создан"
    )

    # Создаём позиции заказа
    for item in cart_items:
        robot = item.robot

        OrderItem.objects.create(
            order=order,
            robot=robot,
            quantity=item.quantity,
            unit_price=robot.price or Decimal("0.00"),
        )

        robot.stock -= item.quantity
        robot.save(update_fields=["stock"])

    # Очищаем корзину
    cart_items.delete()
    cart.is_active = False
    cart.save(update_fields=["is_active"])

    messages.success(request, "Заказ успешно оформлен!")
    return redirect("orders:detail", pk=order.pk)
