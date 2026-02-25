import logging

from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Robot

logger = logging.getLogger("robotshop")


def robot_list(request):
    logger.info(
        "Robot list opened by user=%s",
        request.user if request.user.is_authenticated else "anon",
    )
    robots = Robot.objects.filter(is_active=True).select_related("category", "brand")

    q = request.GET.get("q")
    if q:
        robots = robots.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(brand__name__icontains=q)
        )

    category_slug = request.GET.get("category")
    if category_slug:
        robots = robots.filter(category__slug=category_slug)

    paginator = Paginator(robots, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)

    return render(
        request,
        "catalog/robot_list.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "q": q or "",
        },
    )


def robot_detail(request, slug):
    robot = get_object_or_404(
        Robot.objects.select_related("category", "brand").prefetch_related(
            "tags", "images", "spec_values__specification", "reviews"
        ),
        slug=slug,
        is_active=True,
    )
    avg_rating = robot.reviews.aggregate(avg=Avg("rating"))["avg"]
    return render(
        request,
        "catalog/robot_detail.html",
        {
            "robot": robot,
            "avg_rating": avg_rating,
        },
    )
