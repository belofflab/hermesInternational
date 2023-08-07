from django.shortcuts import render


def index(request):
    return render(request, "main/index.html", context={})

def shops(request):
    return render(request, "main/shops.html", context={})
