from django.shortcuts import render, redirect


def index(request):
    return render(request, "main/index.html", context={})


def about(request):
    return render(request, "main/about.html", context={})


def handler404(request, exception):
    current_language_prefix = request.LANGUAGE_CODE
    return redirect(f"/{current_language_prefix}/")


def handler403(request, exception):
    return render(request, "main/404.html")


def handler500(request):
    return render(request, "main/404.html")
