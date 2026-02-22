from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Robot, Category


def robot_list(request):
    robots = Robot.objects.filter(is_active=True).select_related("category", "brand")

    q = request.GET.get("q")
    if q:
        robots = robots.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(brand__name__icontains=q)
        )

    category_slug = request.GET.get("category")
    if category_slug:
        robots = robots.filter(category__slug=category_slug)

    paginator = Paginator(robots, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)

    return render(request, "catalog/robot_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        "q": q or ""
    })
from django.shortcuts import render, get_object_or_404
from .models import Robot

def robot_detail(request, slug):
    robot = get_object_or_404(
        Robot.objects.select_related("category", "brand").prefetch_related(
            "tags", "images", "spec_values__specification"
        ),
        slug=slug,
        is_active=True,
    )
    return render(request, "catalog/robot_detail.html", {"robot": robot})