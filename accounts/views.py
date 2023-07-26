import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.http.response import JsonResponse

from django.views import View

from . import forms, models

from .services import message

from main.models import Warehouse


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
        last_visit = models.Visits.objects.filter(account=account).latest('last_login')
        context = {"purchases": account.purchases.all()[:5], "last_visit": last_visit}
        return render(request, "accounts/profile.html", context)

    def post(self, request):
        return render(request, "accounts/profile.html", {})


class ProfileWarehouseView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request):
        context = {"warehouses": Warehouse.objects.all()}
        return render(request, "accounts/warehouses.html", context)


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


class InboxView(LoginRequiredMixin, View):
    login_url = "/"

    def get(self, request, *args, **kwargs):
        account = models.Account.objects.get(email=request.user)
        purchase_form = forms.PurchaseForm(request.POST or None)
        return render(
            request,
            "accounts/inbox.html",
            {"purchases": account.purchases.all(), "purchase_form": purchase_form},
        )

    def post(self, request):
        purchase_form = forms.PurchaseForm(request.POST)
        account = models.Account.objects.get(email=request.user)

        new_purchase = purchase_form.save()
        account.purchases.add(new_purchase)

        message.send(
            f"""
Пользователь <b>{account}</b> добавил новую покупку:
Наименование: {new_purchase.name}
Ссылка на товар:  <a href="{new_purchase.link}">click me</a>
Количество: {new_purchase.quantity} шт
Цена: ${new_purchase.price}
Трек номер: {new_purchase.tracking_number}"""
        )

        return render(
            request,
            "accounts/inbox.html",
            {"purchases": account.purchases.all(), "purchase_form": purchase_form},
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
