import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import render

from catalog.models import Brand


logger = logging.getLogger("robotshop")


def home(request):
    logger.info("Home page requested")
    return render(request, "pages/home.html")


def about(request):
    return render(request, "pages/about.html")


def login_page(request):
    return render(request, "pages/login_np.html")


def contacts(request):
    return render(request, "pages/contacts.html")


def delivery(request):
    return render(request, "pages/delivery.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def terms(request):
    return render(request, "pages/terms.html")


def faq(request):
    return render(request, "pages/faq.html")


def blog(request):
    return render(request, "pages/blog.html")


@staff_member_required
def stats_brands(request):
    current_sort = request.GET.get("sort", "count")
    if current_sort == "name":
        brands_qs = Brand.objects.annotate(robot_count=Count("robots")).order_by("name")
    else:
        current_sort = "count"
        brands_qs = Brand.objects.annotate(robot_count=Count("robots")).order_by("-robot_count", "name")

    brands = list(brands_qs)
    total_robots = sum(brand.robot_count for brand in brands)

    top_brands = sorted(brands, key=lambda b: b.robot_count, reverse=True)[:10]
    chart_labels = [brand.name for brand in top_brands]
    chart_values = [brand.robot_count for brand in top_brands]

    return render(
        request,
        "stats/brands.html",
        {
            "brands": brands,
            "total_robots": total_robots,
            "current_sort": current_sort,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
        },
    )


def error_404(request, exception):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)
