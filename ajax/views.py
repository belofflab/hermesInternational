import datetime

from django.contrib.auth import authenticate, login
from accounts.services import message
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.views import View
from django.utils.translation import gettext as _
from decimal import Decimal, InvalidOperation
from main.models import AccountWarehouse, Warehouse
from accounts.models import Account, AccountData, Purchase, Visits, AccountNotifySettings


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
        return JsonResponse({"status": False, "message": _("Некорректный Email или пароль")})


def proceed_signup(request_data: dict):
    if not all([v for v in request_data.values()]):
        return False
    return True


class RegistrationView(View):
    def post(self, request):
        request_data = request.POST
        if not proceed_signup(request_data):
            return JsonResponse({"status": False, "message": _("Некорректные данные")})
        if Account.objects.filter(email=request_data.get("email")).exists():
            return JsonResponse({"status": False, "message": _("Пользователь уже существует")})
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

        return JsonResponse({"status": False, "message": _("Некорректные данные")})


class PurchaseCreateView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        name = request_data.get("name")
        url = request_data.get("url")
        track_number = request_data.get("track_number")
        quantity = request_data.get("quantity")
        try:
            price = Decimal(request_data.get("price"))
        except InvalidOperation:
            return JsonResponse({"status": False, "message": _("Некорректно задана цена")})

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
    
class PurchaseChangeStatusView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        purchase = Purchase.objects.get(id=request_data.get("purchase"))
        purchase.status = request_data.get("status")
        purchase.save()
        return JsonResponse({"status": True, "message": ""})


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
        deliveryMethod = request_data.get("deliveryMethod")

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
        purchase.status = "FORWARDING"
        purchase.delivery_method = deliveryMethod

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


class AccountNotifySettingsView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            settings = AccountNotifySettings.objects.get(account=request.user)
        except AccountNotifySettings.DoesNotExist:
            return JsonResponse({"status": False, "message":"Account Settings does not exists"})
        settings.is_telegram_status = True if request.POST.get('telegram_status') == 'on' else False
        settings.is_email_status = True if request.POST.get('email_status') == 'on' else False
        settings.is_telegram_news = True if request.POST.get('telegram_news') == 'on' else False
        settings.is_email_news = True if request.POST.get('email_news') == 'on' else False
        settings.save()

        return JsonResponse({"status": True, "message": ""})
    

class AccountDataUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        account = Account.objects.get(email=request.user)
        first_name = request_data.get("first_name")
        last_name = request_data.get("last_name")
        sur_name = request_data.get("sur_name")
        country = request_data.get("country")

        account.first_name = first_name
        account.last_name = last_name
        account.sur_name = sur_name
        account.country = country

        account.save()

        return JsonResponse({"status": True, "message":""})
    

class AccountWarehouseCreateView(LoginRequiredMixin, View):
    def post(self, request):
        
        account=request.user,
        address=request.POST.get('street'),
        city=request.POST.get('city'),
        state=request.POST.get('state'),
        zip=request.POST.get('postal_code'),
        phone=request.POST.get('phone')

        return JsonResponse({"status": True, "message":""})