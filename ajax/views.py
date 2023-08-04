import datetime
import json
from django.forms.models import model_to_dict
from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.utils.translation import gettext as _
from django.views import View

from accounts.models import (
    Account,
    AccountData,
    AccountNotifySettings,
    Purchase,
    Visits,
)
from accounts.services import message
from main.models import AccountWarehouse


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
        return JsonResponse(
            {"status": False, "message": _("Некорректный Email или пароль")}
        )


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
            return JsonResponse(
                {"status": False, "message": _("Пользователь уже существует")}
            )
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
        id = request_data.get("id") 

        try:
            price = Decimal(request_data.get("price"))
        except InvalidOperation:
            return JsonResponse(
                {"status": False, "message": _("Некорректно задана цена")}
            )
        
        status = request_data.get("status")
        
        kwargs = {
            "defaults": {
                "name": name,
                "link": url,
                "tracking_number": track_number,
                "quantity": quantity,
                "price": price,
                "status": status
            }
        }
        try:
            id = int(id)
        except ValueError:
            id = None
        if id is not None:
            if isinstance(id, str):
                kwargs["id"] = None
            else:
                kwargs["id"] = id
        else:
            kwargs["id"] = None 

        new_purchase, created = Purchase.objects.update_or_create(**kwargs)
        if created:
            new_purchase.status = "ACCEPTANCE"
            new_purchase.save()

        current_user = Account.objects.get(email=request.user)

        current_user.purchases.add(new_purchase)

        return JsonResponse({"status": True, "data": new_purchase.id})


def serialize_address(address, delivery_method):
    if address is None: return None
    return {
                'id': address.id,
                'phone': address.phone,
                'city': address.city,
                'street': address.street,
                'delivery_method':delivery_method,
                'state': address.state,
                'postal_code': address.postal_code,
                'country': address.country,
            }
    

class PurchaseGetView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        purchaseId = request_data.get("purchaseId")
        addressId = request_data.get("addressId")
        purchase = Purchase.objects.get(id=purchaseId)
        purchase_data = {
            "id": purchase.id,
            "name": purchase.name,
            "link": purchase.link,
            "quantity": purchase.quantity,
            "address": serialize_address(purchase.address, purchase.delivery_method),  # Assuming you want to serialize the address_id.
            "delivery_method": purchase.delivery_method,
            "is_deliveried": purchase.is_deliveried,
            "options": [option.id for option in purchase.options.all()],  # Assuming you want to serialize the option names.
            "price": str(purchase.price),  # Convert DecimalField to string.
            "tracking_number": purchase.tracking_number,
            "status": purchase.status,
            "created": purchase.created.isoformat(),  # Convert DateTimeField to ISO 8601 format.
        }
        
        if addressId is not None:
            try:
                address = AccountData.objects.get(id=addressId)
            except AccountData.DoesNotExist:
                address = None
        else:
            address = None

        response_data = {
            "status": True,
            "purchase": purchase_data,
        }

        if address is not None:
            response_data["address"] = model_to_dict(address)

        return JsonResponse(response_data)


class PurchaseChangeStatusView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        purchase = Purchase.objects.get(id=request_data.get("purchase"))
        purchase.status = request_data.get("status")
        purchase.save()
        return JsonResponse({"status": True})


class AccountDataCreateView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        id = request_data.get('id')
        phone = request_data.get("phone")
        city = request_data.get("city")
        street = request_data.get("street")
        state = request_data.get("state")
        postal_code = request_data.get("postal_code")
        country = request_data.get("country")
        options = request_data.getlist("options[]")
        deliveryMethod = request_data.get("deliveryMethod")
        purchase = Purchase.objects.get(id=request_data.get("purchase"))

        kwargs = {  
            "defaults": {
                'phone': phone,
                'city': city,
                'street': street,
                'delivery_method': deliveryMethod,
                'state': state,
                'postal_code': postal_code,
                'country': country,
            }
        }
        try:
            id = int(id)
        except ValueError:
            id = None
        if id is not None:
            if isinstance(id, str):
                kwargs["id"] = None
            else:
                kwargs["id"] = id
        else:
            kwargs["id"] = None 
        

        new_account, created = AccountData.objects.update_or_create(**kwargs)

        purchase.address = new_account
        purchase.status = "FORWARDING"
        purchase.delivery_method = deliveryMethod

        for option in options:
            purchase.options.add(option)

        purchase.save()

#         message.send(
#             f"""
# Пользователь: <b>{request.user}</b> оформил покупку

# Наименование: {purchase.name}
# Ссылка на товар: <a href="{purchase.link}">{purchase.name}</a>
# Количество: {purchase.quantity}
# Цена: ${purchase.price}
# Трек номер: {purchase.tracking_number}       

# """
#         )

        return JsonResponse({"status": True, "message": ""})


class AccountNotifySettingsView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            settings = AccountNotifySettings.objects.get(account=request.user)
        except AccountNotifySettings.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Account Settings does not exists"}
            )
        settings.is_telegram_status = (
            True if request.POST.get("telegram_status") == "on" else False
        )
        settings.is_email_status = (
            True if request.POST.get("email_status") == "on" else False
        )
        settings.is_telegram_news = (
            True if request.POST.get("telegram_news") == "on" else False
        )
        settings.is_email_news = (
            True if request.POST.get("email_news") == "on" else False
        )
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

        return JsonResponse({"status": True, "message": ""})


class AccountWarehouseCreateView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        address = request_data.get("street")
        city = request_data.get("city")
        state = request_data.get("state")
        zip = request_data.get("postal_code")
        phone = request_data.get("phone")

        AccountWarehouse.objects.create(
            account=Account.objects.get(email=request.user),
            address=address,
            city=city,
            state=state,
            zip=zip,
            phone=phone,
        )

        return JsonResponse({"status": True, "message": ""})


class AccountWarehouseDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        warehouse = request_data.get("warehouse")

        AccountWarehouse.objects.filter(id=warehouse).delete()

        return JsonResponse({"status": True, "message": ""})
