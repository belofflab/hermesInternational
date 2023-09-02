import datetime
import threading
from decimal import Decimal, InvalidOperation

import jwt
from django.conf import settings
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _
from django.views import View

from accounts.models import (Account, AccountData, AccountNotifySettings,
                             Purchase, Visits)
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


        # if not status:
        #     return JsonResponse(
        #         {
        #             "status": False,
        #             "message": _("Пожалуйста, выберите что делаем с заказом"),
        #         }
        #     )

        kwargs = {
            "defaults": {
                "name": name,
                "link": url,
                "tracking_number": track_number,
                "quantity": quantity,
                "price": price,
                "status": status if status == "BUYOUT" else "ACCEPTANCE",
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

        current_user = Account.objects.get(email=request.user)

        current_user.purchases.add(new_purchase)

        return JsonResponse({"status": True, "data": new_purchase.id})


def serialize_address(address, delivery_method):
    if address is None:
        return None
    return {
        "id": address.id,
        "phone": address.phone,
        "city": address.city,
        "street": address.street,
        "delivery_method": delivery_method,
        "state": address.state,
        "postal_code": address.postal_code,
        "country": address.country,
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
            "address": serialize_address(
                purchase.address, purchase.delivery_method
            ),  # Assuming you want to serialize the address_id.
            "delivery_method": purchase.delivery_method,
            "is_deliveried": purchase.is_deliveried,
            "options": [
                option.id for option in purchase.options.all()
            ],  # Assuming you want to serialize the option names.
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


class PurchaseRemoveView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        idx = request_data.get("idx")
        Purchase.objects.filter(id=int(idx)).delete()

        return JsonResponse({"status": True})


class PurchaseChangeStatusView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        purchase = Purchase.objects.get(id=request_data.get("purchase"))
        purchase.status = request_data.get("status")
        purchase.save()
        return JsonResponse({"status": True})


def send_purchase_confirmation_email(purchase, user):
    subject = "Информация о оформлении отправления"
    recipient_email = user.email

    context = {
        "purchase": purchase,
    }

    html_message = render_to_string(
        "ajax/email_templates/purchase_confirmation.html", context
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        "Hermes International <support@hermesinternational.ru>",
        [recipient_email],
        html_message=html_message,
    )


class AccountDataCreateView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        id = request_data.get("id")
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
                "phone": phone,
                "city": city,
                "street": street,
                # 'delivery_method': deliveryMethod,
                "state": state,
                "postal_code": postal_code,
                "country": country,
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

        purchase.options.clear()

        for option in options:
            purchase.options.add(option)

        purchase.save()

        email_thread = threading.Thread(target=send_purchase_confirmation_email, args=(purchase, request.user))
        email_thread.start()
        # TODO
        message.send(
            f"""
Пользователь: <b>{request.user}</b> оформил покупку

Наименование: {purchase.name}
Ссылка на товар: <a href="{purchase.link}">{purchase.name}</a>
Количество: {purchase.quantity}
Цена: ${purchase.price}
Трек номер: {purchase.tracking_number}       

"""
        )

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
    
class AccountPasswordUpdateView(View):
    def post(self, request):
        new_password = request.POST.get('new_password')
        repeat_new_password = request.POST.get('repeat_new_password')
        email = request.POST.get("email")

        if email:
            
            try:
                cur_user = Account.objects.get(email=email)
            except Account.DoesNotExist:
                return JsonResponse({'status': False, 'message': _("Пользователь не найден")})

            if new_password != repeat_new_password:
                return JsonResponse({'status': False, 'message': _("Пароли не совпадают")})

            cur_user.set_password(new_password)
            cur_user.save()

            user = authenticate(request=request, username=email, password=new_password)

            if user:
                login(request=request, user=user)
                return JsonResponse({'status': True})
            
            return JsonResponse({"status": False, 'message': _("Неверный email или пароль")})
        else: 
            new_password = request.POST.get('new_password')
            repeat_new_password = request.POST.get('repeat_new_password')
            if new_password != repeat_new_password:
                return JsonResponse({'status': False, 'message': _("Пароли не совпадают")})

            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

            return JsonResponse({"status": True})
        
class AccountFullPasswordUpdateView(View):
    def post(self, request):
        email = request.POST.get('email')
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return JsonResponse({'status': False, 'message': _('Запрашиваемый пользователь не найден')})
        
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))

        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        token = jwt.encode({'email': email, 'exp': expiration}, settings.SECRET_KEY, algorithm='HS256')

        reset_url = 'https://hermesinternational.ru' + reverse('accounts:password_reset_confirm', args=[uidb64, token])

        current_site = get_current_site(request)
        subject = 'Сброс пароля'
        message = render_to_string('accounts/email/password_reset_request.txt', {
            'user': user,
            'reset_url': reset_url,
            'domain': current_site.domain
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return JsonResponse({'status': True, 'message': _('Ссылка для сброса пароля успешно отправлена')})


class AccountWarehouseCreateView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        user = request.user
        summ_of_warehouse = 50
        if user.balance < summ_of_warehouse:
            return JsonResponse({"status": False, "message": ""})

        user.update_balance(-summ_of_warehouse)
        address = request_data.get("street")
        city = request_data.get("city")
        state = request_data.get("state")
        zip = request_data.get("postal_code")
        phone = request_data.get("phone")

        # AccountWarehouse.objects.create(
        #     account=Account.objects.get(email=request.user),
        #     address=address,
        #     city=city,
        #     state=state,
        #     zip=zip,
        #     phone=phone,
        # )

        return JsonResponse({"status": True, "message": ""})


class AccountWarehouseDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        warehouse = request_data.get("warehouse")

        AccountWarehouse.objects.filter(id=warehouse).delete()

        return JsonResponse({"status": True, "message": ""})


class AccountAvatarChange(View):
    def post(self, request):
        if request.FILES.get("profile_image"):
            user = request.user
            profile_image = request.FILES["profile_image"]
            user.profile_image = profile_image
            user.save()
            return JsonResponse({"image_url": user.profile_image.url})
        return JsonResponse({"error": "Image upload failed"}, status=400)
