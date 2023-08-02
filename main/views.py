from django.shortcuts import render


def index(request):
    return render(request, "main/homepage.html", context={})


def about(request):
    return render(request, "main/about.html", context={})


def pricing(request):
    return render(request, "main/pricing.html", context={})


def reviews(request):
    return render(request, "main/reviews.html", context={})