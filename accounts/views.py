from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.db.models import Q
from django.urls import reverse
from payments.services.crypto import Crypto
from collections import defaultdict
from django.views import View

from . import forms, models

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
            "page": "profile"
        }
        return render(request, "accounts/profile.html", context)

    def post(self, request):
        return render(request, "accounts/profile.html", {})


class ProfileWarehouseView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        context = {"warehouses": Warehouse.objects.all(), "page": "warehouses"}
        return render(request, "accounts/warehouses.html", context)


class ProfilePaymentView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        return render(request, "accounts/payment.html", context={"page": "payment"})

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
            request, "accounts/packages.html", context={"purchases": purchases, "page":"packages"}
        )


def proceed_signup(request_data: dict):
    if not all([v for v in request_data.values()]):
        return False
    return True


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse("main:index"))
    
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
                "page": "inbox"
            },
        )


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


def get_buyout_items_by_category():
    # First, retrieve all the Buyout objects, prefetching the related category
    buyouts = models.Buyout.objects.select_related("category").filter(
        category__is_visible=True
    )

    # Organize the items by category in a dictionary
    category_items_dict = defaultdict(list)

    for buyout in buyouts:
        category_name = buyout.category.name
        item_info = {
            "name": buyout.name,
            "percent": buyout.percent,
        }
        category_items_dict[category_name].append(item_info)

    # Sort categories alphabetically and return the result
    sorted_category_items_dict = dict(
        sorted(category_items_dict.items(), key=lambda x: x[0].lower())
    )

    return sorted_category_items_dict


class BuyOutView(LoginRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            "accounts/buyout.html",
            context={"buyout": get_buyout_items_by_category(), "page":"buyout"},
        )
