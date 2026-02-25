from django.http import JsonResponse


def api_success(data, status=200):
    return JsonResponse(
        {
            "ok": True,
            "data": data,
        },
        status=status,
    )


def api_error(code, message, status=400, details=None):
    payload = {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details:
        payload["error"]["details"] = details
    return JsonResponse(payload, status=status)
