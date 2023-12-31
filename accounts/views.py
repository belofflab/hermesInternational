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
from payments.models import Invoice
from .services.mail import get_email
from . import forms, models
from ajax.tasks import send_email
from django.core.paginator import Paginator
from main.models import Warehouse, AccountWarehouse, WarehouseShop

crypto = Crypto(token=settings.CRYPTO_BOT_TOKEN)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def test(request):
    send_email(
        body="123",
        subject="123",
        recipients=[
            "belofflab@gmail.com",
        ],
    )
    return {""}


class ProfileView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        account = models.Account.objects.get(email=request.user)
        try:
            settings = models.AccountNotifySettings.objects.get(account=request.user)
        except models.AccountNotifySettings.DoesNotExist:
            settings = {}
        try:
            last_visit = models.Visits.objects.filter(account=account).latest(
                "last_login"
            )
        except models.Visits.DoesNotExist:
            last_visit = {}
        context = {
            "purchases": account.purchases.all()[:5],
            "last_visit": last_visit,
            "settings": settings,
            "page": "profile",
        }
        return render(request, "accounts/profile.html", context)

    def post(self, request):
        return render(request, "accounts/profile.html", {})


class ProfileAdminView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        if not request.user.is_admin:
            return redirect(reverse("main:index"))
        
        accounts = models.Account.objects.all()
        purchase_per_accounts = []
        for account in accounts:
            purchase_list = account.purchases.prefetch_related("address").all()
            for purchase in purchase_list:
                purchase.account = account
            purchase_per_accounts.extend(purchase_list)

        paginator_purchase = Paginator(purchase_per_accounts, 20)          

        purchase_per_accounts_page = paginator_purchase.get_page(request.GET.get('purchase_page'))

        context = {
                "purchase_per_accounts": purchase_per_accounts_page,
                "purchase_statuses": models.purchase_statuses,
                "page": "profile_admin"
            }
        return render(request, "accounts/admin_profile_purchases.html", context)
    
class ProfileAdminUsersView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        if not request.user.is_admin:
            return redirect(reverse("main:index"))
        
        accounts = models.Account.objects.order_by("user_status_last_update").all()
        paginator_accounts = Paginator(accounts, 20)   
        accounts_page = paginator_accounts.get_page(request.GET.get('account_page'))


        context = {
                "accounts": accounts_page,
                "page": "profile_admin_users",
                "users_statuses": models.users_statuses,
            }
        return render(request, "accounts/admin_profile_users.html", context)
    
class ProfileAdminWarehousesView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        if not request.user.is_admin:
            return redirect(reverse("main:index"))
        
        warehouses = AccountWarehouse.objects.all()

        context = {
                "warehouses": warehouses,
                "page": "profile_admin_warehouses",
            }
        return render(request, "accounts/admin_profile_warehouses.html", context)


class ProfileWarehouseView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        account_warehouses = AccountWarehouse.objects.filter(account=request.user).all()
        warehouses = Warehouse.objects.all()

        warehouse_shops = WarehouseShop.objects.filter(
            content_type__model__in=["warehouse", "accountwarehouse"]
        )

        for warehouse in warehouses:
            warehouse.warehouse_shops = [
                shop
                for shop in warehouse_shops
                if shop.object_id == warehouse.id
                and shop.content_type.model == warehouse.__class__.__name__.lower()
            ]
        for account_warehouse in account_warehouses:
            account_warehouse.warehouse_shops = [
                shop
                for shop in warehouse_shops
                if shop.object_id == account_warehouse.id
                and shop.content_type.model
                == account_warehouse.__class__.__name__.lower()
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


class ProfilePricesView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        return render(request, "accounts/prices.html", context={"page": "prices"})


class ProfilePackagesView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        purchases = models.Purchase.objects.prefetch_related("photos").filter(
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
    login_url = "/"

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
                    Q(status="BUYOUT") | Q(status="ACCEPTANCE") | Q(status="FORWARDING")
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
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if decoded_token["email"] != user.email:
                raise jwt.ExpiredSignatureError()
        except jwt.ExpiredSignatureError:
            errors.append("Токен истёк")

        return render(
            request,
            "accounts/change_password.html",
            context={"errors": errors, "email": user.email},
        )


def get_buyout_items_by_category():
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
    login_url = "/"

    def get(self, request):
        return render(
            request,
            "accounts/buyout.html",
            context={"buyout": get_buyout_items_by_category(), "page": "buyout"},
        )


class MailListView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        if not request.user.is_admin:
            return redirect("accounts:profile")
        email_list = get_email()
        return render(
            request,
            "accounts/all_mail.html",
            context={"email_list": email_list, "page": "buyout"},
        )


class MailSendView(LoginRequiredMixin, View):
    login_url = "/"

    def post(self, request):
        if not request.user.is_admin:
            return redirect(reverse("accounts:profile"))
        request_data = request.POST

        recipient = request_data.get("recipient")
        subject = request_data.get("subject")
        mymessage = request_data.get("mymessage")

        send_email(body=mymessage, subject=subject, recipients=[recipient])

        return redirect(reverse("accounts:mail_list"))


class ProfileSimplePurchaseView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        return render(
            request,
            "accounts/simple_purchase.html",
            context={"page": "simple_purchase"},
        )
