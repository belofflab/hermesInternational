from django.shortcuts import render

from django.core.mail import send_mail


def index(request):
    return render(request, "main/index.html", context={})

def shops(request):
    return render(request, "main/shops.html", context={})

def email_test(request):
    send_mail("123", "123", "Hermes International <support@hermesinternational.ru>", recipient_list=["belofflab@gmail.com"])