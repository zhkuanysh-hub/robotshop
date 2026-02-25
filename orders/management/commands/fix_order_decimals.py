from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.core.management.base import BaseCommand
from django.db import connection, transaction


MAX_DECIMAL = Decimal("99999999.99")
MIN_DECIMAL = Decimal("0")


def parse_decimal(raw_value):
    if raw_value is None:
        return None
    value = str(raw_value).strip()
    if not value or value.lower() in {"none", "null"}:
        return None
    try:
        parsed = Decimal(value.replace(",", "."))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return parsed.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Command(BaseCommand):
    help = "Fix invalid or overflowing decimal values in orders/orderitems."

    @transaction.atomic
    def handle(self, *args, **options):
        fixed_items = 0
        fixed_orders = 0

        with connection.cursor() as cursor:
            cursor.execute("SELECT id, CAST(unit_price AS TEXT) FROM orders_orderitem")
            item_rows = cursor.fetchall()
            for item_id, unit_price_raw in item_rows:
                parsed = parse_decimal(unit_price_raw)
                if parsed is None or parsed < MIN_DECIMAL or parsed > MAX_DECIMAL:
                    cursor.execute(
                        "UPDATE orders_orderitem SET unit_price=%s WHERE id=%s",
                        ["0.00", item_id],
                    )
                    fixed_items += 1

            cursor.execute("SELECT id, CAST(total_amount AS TEXT) FROM orders_order")
            order_rows = cursor.fetchall()
            for order_id, total_raw in order_rows:
                parsed_total = parse_decimal(total_raw)
                total_valid = (
                    parsed_total is not None
                    and MIN_DECIMAL <= parsed_total <= MAX_DECIMAL
                )
                if total_valid:
                    continue

                cursor.execute(
                    """
                    SELECT CAST(unit_price AS TEXT), quantity
                    FROM orders_orderitem
                    WHERE order_id=%s
                    """,
                    [order_id],
                )
                total = Decimal("0.00")
                for unit_price_raw, quantity in cursor.fetchall():
                    parsed_price = parse_decimal(unit_price_raw) or Decimal("0.00")
                    total += parsed_price * Decimal(quantity or 0)

                if total < MIN_DECIMAL or total > MAX_DECIMAL:
                    total = Decimal("0.00")

                cursor.execute(
                    "UPDATE orders_order SET total_amount=%s WHERE id=%s",
                    [str(total.quantize(Decimal("0.01"))), order_id],
                )
                fixed_orders += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Fixed order items: {fixed_items}. Fixed orders: {fixed_orders}."
            )
        )
