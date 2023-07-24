from django.shortcuts import render

def index(request): return render(request, "main/index.html", context={})

def about(request): return render(request, "main/about.html", context={})
# def login(request): return render(request, "main/login.html", context={})
# def signup(request): return render(request, "main/signup.html", context={})
def pricing(request): return render(request, "main/pricing.html", context={})
def reviews(request): return render(request, "main/reviews.html", context={})
# def reset_password(request): return render(request, "main/reset-password.html", context={})
