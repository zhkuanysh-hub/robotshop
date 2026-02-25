import json
from decimal import Decimal, InvalidOperation
from json import JSONDecodeError

from django.db.models import Q
from django.http import Http404
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from catalog.models import Brand, Category, Robot

from .utils import api_error, api_success


def parse_json_body(request):
    raw = (request.body or b"").decode("utf-8").strip()
    if not raw:
        return {}
    return json.loads(raw)


def parse_decimal(value, field_name):
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}.")
    return parsed


def ensure_staff(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return api_error("forbidden", "Staff access required.", status=403)
    return None


def unique_slug(base_slug, exclude_pk=None):
    slug = base_slug or "robot"
    candidate = slug
    index = 2
    queryset = Robot.objects.all()
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)
    while queryset.filter(slug=candidate).exists():
        candidate = f"{slug}-{index}"
        index += 1
    return candidate


def serialize_robot(robot, include_tags=False):
    data = {
        "id": robot.id,
        "name": robot.name,
        "slug": robot.slug,
        "description": robot.description,
        "price": str(robot.price),
        "stock": robot.stock,
        "is_active": robot.is_active,
        "brand": {"id": robot.brand_id, "name": robot.brand.name},
        "category": {
            "id": robot.category_id,
            "name": robot.category.name,
            "slug": robot.category.slug,
        },
    }
    if include_tags:
        data["tags"] = [{"id": tag.id, "name": tag.name} for tag in robot.tags.all()]
    return data


@csrf_exempt
def robots(request):
    if request.method not in {"GET", "POST"}:
        return api_error("method_not_allowed", "Method not allowed", status=405)

    if request.method == "GET":
        robots_qs = Robot.objects.select_related("brand", "category").all()

        q = request.GET.get("q", "").strip()
        if q:
            robots_qs = robots_qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

        brand = request.GET.get("brand")
        if brand:
            robots_qs = robots_qs.filter(brand_id=brand)

        category = request.GET.get("category")
        if category:
            robots_qs = robots_qs.filter(category_id=category)

        min_price = request.GET.get("min_price")
        if min_price:
            try:
                robots_qs = robots_qs.filter(price__gte=parse_decimal(min_price, "min_price"))
            except ValueError as exc:
                return api_error("bad_request", str(exc), status=400)

        max_price = request.GET.get("max_price")
        if max_price:
            try:
                robots_qs = robots_qs.filter(price__lte=parse_decimal(max_price, "max_price"))
            except ValueError as exc:
                return api_error("bad_request", str(exc), status=400)

        allowed_ordering = {"price", "-price", "created_at", "-created_at", "name", "-name"}
        ordering = request.GET.get("ordering", "-created_at")
        if ordering not in allowed_ordering:
            return api_error(
                "bad_request",
                "Invalid ordering.",
                status=400,
                details={"allowed": sorted(allowed_ordering)},
            )
        robots_qs = robots_qs.order_by(ordering)

        try:
            page = max(1, int(request.GET.get("page", 1)))
            page_size = int(request.GET.get("page_size", 10))
            if page_size < 1:
                page_size = 10
            page_size = min(page_size, 100)
        except ValueError:
            return api_error("bad_request", "Invalid page or page_size.", status=400)

        total = robots_qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = [serialize_robot(robot) for robot in robots_qs[start:end]]

        return api_success(
            {
                "count": total,
                "page": page,
                "page_size": page_size,
                "results": items,
            }
        )

    forbidden = ensure_staff(request)
    if forbidden:
        return forbidden

    try:
        payload = parse_json_body(request)
    except JSONDecodeError:
        return api_error("bad_request", "Invalid JSON body.", status=400)

    required_fields = ["name", "price", "brand_id", "category_id"]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        return api_error(
            "bad_request",
            "Missing required fields.",
            status=400,
            details={"missing": missing},
        )

    try:
        price = parse_decimal(payload.get("price"), "price")
    except ValueError as exc:
        return api_error("bad_request", str(exc), status=400)
    if price < 0:
        return api_error("bad_request", "price must be >= 0.", status=400)

    try:
        brand = Brand.objects.get(pk=payload.get("brand_id"))
        category = Category.objects.get(pk=payload.get("category_id"))
    except (Brand.DoesNotExist, Category.DoesNotExist):
        return api_error("bad_request", "Invalid brand_id or category_id.", status=400)

    raw_slug = (payload.get("slug") or "").strip() or slugify(payload.get("name", ""))
    generated_slug = unique_slug(raw_slug)

    robot = Robot.objects.create(
        name=payload.get("name", "").strip(),
        slug=generated_slug,
        description=payload.get("description", ""),
        price=price,
        stock=int(payload.get("stock", 0)),
        is_active=bool(payload.get("is_active", True)),
        brand=brand,
        category=category,
    )
    robot = Robot.objects.select_related("brand", "category").get(pk=robot.pk)
    return api_success(serialize_robot(robot), status=201)


@csrf_exempt
def robot_detail(request, robot_id):
    if request.method not in {"GET", "PUT", "DELETE"}:
        return api_error("method_not_allowed", "Method not allowed", status=405)

    try:
        robot = (
            Robot.objects.select_related("brand", "category")
            .prefetch_related("tags")
            .get(pk=robot_id)
        )
    except Robot.DoesNotExist:
        return api_error("not_found", "Robot not found.", status=404)
    except Http404:
        return api_error("not_found", "Robot not found.", status=404)

    if request.method == "GET":
        return api_success(serialize_robot(robot, include_tags=True))

    forbidden = ensure_staff(request)
    if forbidden:
        return forbidden

    if request.method == "DELETE":
        robot.delete()
        return api_success({"deleted": True})

    try:
        payload = parse_json_body(request)
    except JSONDecodeError:
        return api_error("bad_request", "Invalid JSON body.", status=400)

    if "name" in payload:
        robot.name = str(payload["name"]).strip()

    if "description" in payload:
        robot.description = payload["description"] or ""

    if "price" in payload:
        try:
            price = parse_decimal(payload["price"], "price")
        except ValueError as exc:
            return api_error("bad_request", str(exc), status=400)
        if price < 0:
            return api_error("bad_request", "price must be >= 0.", status=400)
        robot.price = price

    if "stock" in payload:
        try:
            robot.stock = max(0, int(payload["stock"]))
        except (TypeError, ValueError):
            return api_error("bad_request", "Invalid stock.", status=400)

    if "is_active" in payload:
        robot.is_active = bool(payload["is_active"])

    if "brand_id" in payload:
        try:
            robot.brand = Brand.objects.get(pk=payload["brand_id"])
        except Brand.DoesNotExist:
            return api_error("bad_request", "Invalid brand_id.", status=400)

    if "category_id" in payload:
        try:
            robot.category = Category.objects.get(pk=payload["category_id"])
        except Category.DoesNotExist:
            return api_error("bad_request", "Invalid category_id.", status=400)

    if "slug" in payload or "name" in payload:
        requested_slug = (payload.get("slug") or "").strip() or slugify(robot.name)
        robot.slug = unique_slug(requested_slug, exclude_pk=robot.pk)

    robot.save()
    robot = (
        Robot.objects.select_related("brand", "category")
        .prefetch_related("tags")
        .get(pk=robot.pk)
    )
    return api_success(serialize_robot(robot, include_tags=True))


def brands(request):
    if request.method != "GET":
        return api_error("method_not_allowed", "Method not allowed", status=405)
    data = list(Brand.objects.order_by("name").values("id", "name"))
    return api_success(data)


def categories(request):
    if request.method != "GET":
        return api_error("method_not_allowed", "Method not allowed", status=405)
    data = list(Category.objects.order_by("name").values("id", "name", "slug"))
    return api_success(data)
