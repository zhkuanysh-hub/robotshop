from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include(("apps.core.urls", "core"), namespace="core")),

    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("catalog/", include(("catalog.urls", "catalog"), namespace="catalog")),
    path("cart/", include(("cart.urls", "cart"), namespace="cart")),
    path("orders/", include(("orders.urls", "orders"), namespace="orders")),
    path("reviews/", include(("reviews.urls", "reviews"), namespace="reviews")),
    path("wishlist/", include(("wishlist.urls", "wishlist"), namespace="wishlist")),
    path("inventory/", include(("inventory.urls", "inventory"), namespace="inventory")),
    path("payments/", include(("payments.urls", "payments"), namespace="payments")),
    path("shipping/", include(("shipping.urls", "shipping"), namespace="shipping")),
    path("api/", include(("api.urls", "api"), namespace="api")),
]