from django.shortcuts import render

def index(request):
    return render(request, "main/index.html", context={})


def about(request):
    return render(request, "main/about.html", context={})


def handler404(request, exception): 
    return render(request, "main/404.html")

def handler403(request, exception): 
    return render(request, "main/404.html")

def handler500(request): 
    return render(request, "main/404.html")