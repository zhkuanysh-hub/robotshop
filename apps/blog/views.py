from django.shortcuts import render

def post_list(request):
    return render(request, "blog/list.html")

def post_detail(request, slug):
    return render(request, "blog/detail.html", {"slug": slug})


