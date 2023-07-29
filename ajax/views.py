import datetime

from django.contrib.auth import authenticate, login
from accounts.services import message
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.views import View
from decimal import Decimal, InvalidOperation

from accounts.models import Account, AccountData, Purchase, Visits


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class LoginView(View):
    def post(self, request, *args, **kwargs):
        request_data = request.POST
        email = request_data.get("email")
        password = request_data.get("password")
        user = authenticate(email=email, password=password)
        if user:
            login(request=request, user=user)
            Visits.objects.update_or_create(
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
        if Account.objects.filter(email=request_data.get("email")).exists():
            return JsonResponse({"status": False, "message": "User already exists"})
        new_user = Account()
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
            Visits.objects.update_or_create(
                account=user,
                last_login=datetime.datetime.now(),
                ip=get_client_ip(request),
            )
            return JsonResponse({"status": True, "message": ""})

        return JsonResponse({"status": False, "message": "Invalid Credentials"})


class PurchaseCreateView(LoginRequiredMixin, View):
    def post(self, request):
        print(request.user)
        request_data = request.POST
        name = request_data.get("name")
        url = request_data.get("url")
        track_number = request_data.get("track_number")
        quantity = request_data.get("quantity")
        try:
            price = Decimal(request_data.get("price"))
        except InvalidOperation:
            return JsonResponse({"status": False, "message": "Неверная цена"})

        status = request_data.get("status")

        new_purchase = Purchase.objects.create(
            name=name,
            link=url,
            quantity=quantity,
            price=price,
            tracking_number=track_number,
            status=status,
        )

        current_user = Account.objects.get(email=request.user)

        current_user.purchases.add(new_purchase)

        return JsonResponse({"status": True, "data": new_purchase.id})


class AccountDataCreateView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        phone = request_data.get("phone")
        city = request_data.get("city")
        street = request_data.get("street")
        state = request_data.get("state")
        postal_code = request_data.get("postal_code")
        country = request_data.get("country")
        options = request_data.getlist("options[]")

        purchase = Purchase.objects.get(id=request_data.get("purchase"))

        new_account = AccountData.objects.create(
            phone=phone,
            city=city,
            street=street,
            state=state,
            postal_code=postal_code,
            country=country,
        )

        purchase.address = new_account

        for option in options:
            purchase.options.add(option)

        purchase.save()


        message.send(f"""
Пользователь: <b>{request.user}</b> оформил покупку

Наименование: {purchase.name}
Ссылка на товар: <a href="{purchase.link}">{purchase.name}</a>
Количество: {purchase.quantity}
Цена: ${purchase.price}
Трек номер: {purchase.tracking_number}       

""")



        return JsonResponse({"status": True, "message": ""})
