import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.http.response import JsonResponse
from django.db.models import Q
from django.urls import reverse
from payments.services.crypto import Crypto

from django.views import View

from . import forms, models

from .services import message

from main.models import Warehouse

crypto = Crypto(token="110981:AA3FManAQxim0xd6CNZF8zf1uzUIziDbe5d")


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class ProfileView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        account = models.Account.objects.get(email=request.user)
        try:
            settings = models.AccountNotifySettings.objects.get(account=request.user)
        except models.AccountNotifySettings.DoesNotExist:
            settings = {}
        last_visit = models.Visits.objects.filter(account=account).latest("last_login")
        context = {
            "purchases": account.purchases.all()[:5],
            "last_visit": last_visit,
            "settings": settings,
        }
        return render(request, "accounts/profile.html", context)

    def post(self, request):
        return render(request, "accounts/profile.html", {})


class ProfileWarehouseView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        context = {"warehouses": Warehouse.objects.all()}
        return render(request, "accounts/warehouses.html", context)


class ProfilePaymentView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        return render(request, "accounts/payment.html")

    def post(self, request):
        request_data = request.POST
        amount = request_data.get("amount")
        receipt = crypto.createInvoice("USDT", amount=amount)
        if receipt.get("ok"):
            return render(
                request,
                "accounts/pay.html",
                context={"pay_url": receipt["result"].get("pay_url"), "amount": amount},
            )
        return redirect(reverse("accounts:payment"))


class ProfilePackagesView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        purchases = models.Purchase.objects.filter(
            Q(account=request.user) & Q(status="FORWARDING")
        )
        return render(
            request, "accounts/packages.html", context={"purchases": purchases}
        )


class LoginView(View):
    def post(self, request, *args, **kwargs):
        request_data = request.POST
        email = request_data.get("email")
        password = request_data.get("password")
        user = authenticate(email=email, password=password)
        if user:
            login(request=request, user=user)
            models.Visits.objects.update_or_create(
                account=user,
                last_login=datetime.datetime.now(),
                ip=get_client_ip(request),
            )
            return JsonResponse({"status": True, "message": ""})
        return JsonResponse({"status": False, "message": "Invalid email or password"})


def proceed_signup(request_data: dict):
    if not all([v for v in request_data.values()]):
        return False
    return True


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse("main:index"))


class RegistrationView(View):
    def post(self, request):
        request_data = request.POST
        if not proceed_signup(request_data):
            return JsonResponse({"status": False, "message": "Invalid Credentials"})
        if models.Account.objects.filter(email=request_data.get("email")).exists():
            return JsonResponse({"status": False, "message": "User already exists"})
        new_user = models.Account()
        new_user.email = request_data.get("email")
        new_user.first_name = request_data.get("first_name")
        new_user.last_name = request_data.get("last_name")
        new_user.country = request_data.get("country")
        new_user.save()
        new_user.set_password(request_data.get("password"))
        new_user.save()
        user = authenticate(
            email=request_data.get("email"),
            password=request_data.get("password"),
        )
        if user:
            login(request=request, user=user)
            models.Visits.objects.update_or_create(
                account=user,
                last_login=datetime.datetime.now(),
                ip=get_client_ip(request),
            )
            return JsonResponse({"status": True, "message": ""})
        return JsonResponse({"status": False, "message": "Invalid Credentials"})


class CollectParcelView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request, *args, **kwargs):
        return render(request, "accounts/collect_parcel.html")


class PurchaseDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        try:
            purchase = models.Purchase.objects.get(id=pk)
        except models.Purchase.DoesNotExist:
            return redirect(reverse("accounts:inbox"))
        return render(
            request, "accounts/inbox-detail.html", context={"purchase": purchase}
        )


class InboxView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request, *args, **kwargs):
        account = models.Account.objects.get(email=request.user)
        purchase_form = forms.PurchaseForm(request.POST or None)
        return render(
            request,
            "accounts/inbox.html",
            {
                "purchases": account.purchases.filter(
                    Q(status="BUYOUT") | Q(status="ACCEPTANCE")
                ).all(),
                "purchase_form": purchase_form,
            },
        )


class ProfileOutboxView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request, *args, **kwargs):
        return render(request, "accounts/outbox.html", {})


class ResetPasswordView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = forms.ResetPasswordForm(request.POST or None)

        context = {"form": form, "title": "res"}
        return render(request, "accounts/reset-password.html", context)

    def post(self, request, *args, **kwargs):
        form = forms.ResetPasswordForm(request.POST)
        if form.is_valid():
            user = models.Account.objects.get(username=request.user)
            new_password = form.cleaned_data["new_password"]
            user.set_password(new_password)
            user.save()
            return redirect("/accounts/logout/")

        context = {"form": form, "title": "Sign Up"}
        return render(request, "accounts/reset-password.html", context)


def buyout(request):
    return render(request, "accounts/buyout.html", context={})
