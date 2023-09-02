import jwt
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.db.models import Q
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse
from django.conf import settings
from payments.services.crypto import Crypto
from collections import defaultdict
from django.views import View
from itertools import chain
from payments.models import Invoice

from . import forms, models

from main.models import Warehouse, AccountWarehouse, WarehouseShop

crypto = Crypto(token=settings.CRYPTO_BOT_TOKEN)


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
            "page": "profile",
        }
        return render(request, "accounts/profile.html", context)

    def post(self, request):
        return render(request, "accounts/profile.html", {})


class ProfileWarehouseView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        account_warehouses = AccountWarehouse.objects.filter(account=request.user).all()
        warehouses = Warehouse.objects.all()

        warehouse_shops = WarehouseShop.objects.filter(
            content_type__model__in=["warehouse" ,"accountwarehouse"]
        )


        for warehouse in warehouses:
            warehouse.warehouse_shops = [
                shop for shop in warehouse_shops
                if shop.object_id == warehouse.id
                and shop.content_type.model == warehouse.__class__.__name__.lower()
            ]
        for account_warehouse in account_warehouses:
            account_warehouse.warehouse_shops = [
                shop for shop in warehouse_shops
                if shop.object_id == account_warehouse.id
                and shop.content_type.model == account_warehouse.__class__.__name__.lower()
            ]


        context = {
            "account_warehouses": account_warehouses,
            "warehouses": warehouses,
            "page": "warehouses",
        }
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
            result = receipt.get("result")
            new_invoice = Invoice.objects.create(
                account=request.user,
                invoice_id=result.get("invoice_id"),
                asset=result.get("asset"),
                amount=result.get("amount"),
                pay_url=result.get("pay_url"),
                status=result.get("status"),
                created_at=result.get("created_at"),
            )
            invoice_detail_url = reverse(
                "payments:invoice_detail", kwargs={"invoice_slug": new_invoice.slug}
            )
            return redirect(invoice_detail_url)
        return render(request, "accounts/payment.html", context={"page": "payment"})


class ProfilePackagesView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        purchases = models.Purchase.objects.filter(
            Q(account=request.user) & Q(status="FORWARDING")
        )
        return render(
            request,
            "accounts/packages.html",
            context={"purchases": purchases, "page": "packages"},
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
    login_url="/"
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
                "page": "inbox",
            },
        )


class PasswordResetConfirmView(View):
    def get(self, request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64).decode()
        user = models.Account.objects.get(pk=uid)
        errors = []
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            if decoded_token['email'] != user.email:
                raise jwt.ExpiredSignatureError()
        except jwt.ExpiredSignatureError:
            errors.append("Токен истёк")
            
        return render(request, "accounts/change_password.html", context={"errors": errors, "email": user.email})



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
    login_url="/"
    def get(self, request):
        return render(
            request,
            "accounts/buyout.html",
            context={"buyout": get_buyout_items_by_category(), "page": "buyout"},
        )


class ProfileSimplePurchaseView(LoginRequiredMixin, View):
    login_url="/"
    def get(self, request):
        return render(
            request,
            "accounts/simple_purchase.html",
            context={"page": "simple_purchase"},
        )