import datetime
import re
from decimal import Decimal, InvalidOperation
import os
import jwt
from django.conf import settings
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _
from django.views import View

from accounts.models import (
    Account,
    AccountData,
    AccountNotifySettings,
    Purchase,
    PurchasePhoto,
    Visits,
)
from main.models import AccountWarehouse, Warehouse, WarehouseShop
from payments.models import Invoice, Service
from payments.services.crypto import Crypto

from .tasks import notify_admin_by_telegram, send_email

crypto = Crypto(token=settings.CRYPTO_BOT_TOKEN)


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


def update_warehouse_quantity(url: str, shops):
    match = re.search(r"(www\.)?(\w+\.\w+)", url)
    matched_shop = match.group(2)

    for shop in shops:
        if matched_shop.startswith(shop.name):
            shop.quantity = shop.quantity + 1
            shop.save()


class PurchaseCreateView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        name = request_data.get("name")
        url = request_data.get("url")
        track_number = request_data.get("track_number")
        quantity = request_data.get("quantity")
        warehouseModel = request_data.get("warehouseModel")
        warehouseId = request_data.get("warehouseId")
        warehouses = {"Warehouse": Warehouse, "AccountWarehouse": AccountWarehouse}
        warehouse = warehouses[warehouseModel].objects.get(id=warehouseId)
        shops = WarehouseShop.objects.filter(
            content_type=ContentType.objects.get_for_model(warehouses[warehouseModel]),
            object_id=warehouseId,
        ).all()
        update_warehouse_quantity(url=url, shops=shops)
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
                "delivery_warehouse_type": ContentType.objects.get_for_model(warehouse),
                "delivery_warehouse_id": warehouse.id,
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

        if status == "BUYOUT":
            notify_admin_by_telegram(
                f"""
Пользователь: <b>{request.user}</b> оформил покупку

Наименование: {new_purchase.name}
Ссылка на товар: <a href="{new_purchase.link}">{new_purchase.name}</a>
Количество: {new_purchase.quantity}
Цена: ${new_purchase.price}
Трек номер: {new_purchase.tracking_number}       

"""
            )

            subject = _("Информация об оформлении отправления")
            html_message = render_to_string(
                "ajax/email/purchase_confirmation.html",
                {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "name": new_purchase.name,
                    "link": new_purchase.link,
                    "quantity": new_purchase.quantity,
                    "price": new_purchase.price,
                    "tracking_number": new_purchase.tracking_number,
                },
            )

            send_email(
                body=html_message, subject=subject, recipients=[request.user.email]
            )

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
            "address": serialize_address(purchase.address, purchase.delivery_method),
            "delivery_method": purchase.delivery_method,
            "is_deliveried": purchase.is_deliveried,
            "options": [option.id for option in purchase.options.all()],
            "price": str(purchase.price),
            "tracking_number": purchase.tracking_number,
            "status": purchase.status,
            "created": purchase.created.isoformat(),
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


def create_invoice(request, c_service: Service, purchase: Purchase, amount: str):
    if purchase.invoice_id:
        c_invoice = Invoice.objects.get(invoice_id=purchase.invoice_id)
        if c_invoice.status == "active" or c_invoice.status == "PAID":
            invoice_detail_url = reverse(
                "payments:invoice_detail", kwargs={"invoice_slug": c_invoice.slug}
            )
            return invoice_detail_url
    receipt = crypto.createInvoice("USDT", amount=amount)
    if receipt.get("ok"):
        result = receipt.get("result")
        new_invoice = Invoice.objects.create(
            account=request.user,
            invoice_id=result.get("invoice_id"),
            service=c_service,
            asset=result.get("asset"),
            amount=result.get("amount"),
            pay_url=result.get("pay_url"),
            status=result.get("status"),
            created_at=result.get("created_at"),
        )
        purchase.invoice_id = new_invoice.invoice_id
        purchase.save()

        invoice_detail_url = reverse(
            "payments:invoice_detail", kwargs={"invoice_slug": new_invoice.slug}
        )
        return invoice_detail_url
    return ""


class PurchasePayView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        idx = request_data.get("purchase")
        try:
            c_service = Service.objects.filter(
                name__startswith="Пересыл посылки"
            ).first()
        except Service.DoesNotExist:
            c_service = None
        if not c_service:
            return JsonResponse({"status": False})
        purchase = Purchase.objects.get(id=idx)
        pay_url = create_invoice(
            request=request,
            c_service=c_service,
            purchase=purchase,
            amount=str(c_service.price),
        )

        return JsonResponse({"status": True, "pay_url": pay_url})


class PurchaseUpdateStatusView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        idx = request_data.get("purchase")
        purchase = Purchase.objects.get(id=int(idx))
        purchase.is_deliveried = True
        purchase.save()
        notify_admin_by_telegram(
            f"""
Пользователь: <b>{request.user}</b> поставил статус покупки на доставлена

Ссылка на панель: {f"https://hermesinternational.ru/UQhCgbBPEuPhAbAPfwbTaX/accounts/purchase/{purchase.id}/change/"}
"""
        )
        return JsonResponse({"status": True})


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
        id = request_data.get("id")
        first_name = request_data.get("first_name")
        last_name = request_data.get("last_name")
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
                "first_name": first_name,
                "last_name": last_name,
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

        request.user.addresses.add(new_account)
        request.user.save()

        subject = _("Информация об оформлении отправления")
        html_message = render_to_string(
                "ajax/email/purchase_confirmation.html",
                {
                    "first_name": purchase.address.first_name,
                    "last_name": purchase.address.last_name,
                    "name": purchase.name,
                    "link": purchase.link,
                    "quantity": purchase.quantity,
                    "price": purchase.price,
                    "tracking_number": purchase.tracking_number,
                },
            )

        send_email(body=html_message, subject=subject, recipients=[request.user.email])
        notify_admin_by_telegram(
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

        account.first_name = request_data.get("first_name")
        account.last_name = request_data.get("last_name")
        account.sur_name = request_data.get("sur_name")
        account.country = request_data.get("country")

        account.save()

        return JsonResponse({"status": True, "message": ""})


class AccountPasswordUpdateView(View):
    def post(self, request):
        new_password = request.POST.get("new_password")
        repeat_new_password = request.POST.get("repeat_new_password")
        email = request.POST.get("email")

        if email:
            try:
                cur_user = Account.objects.get(email=email)
            except Account.DoesNotExist:
                return JsonResponse(
                    {"status": False, "message": _("Пользователь не найден")}
                )

            if new_password != repeat_new_password:
                return JsonResponse(
                    {"status": False, "message": _("Пароли не совпадают")}
                )

            cur_user.set_password(new_password)
            cur_user.save()

            user = authenticate(request=request, username=email, password=new_password)

            if user:
                login(request=request, user=user)
                return JsonResponse({"status": True})

            return JsonResponse(
                {"status": False, "message": _("Неверный email или пароль")}
            )
        else:
            new_password = request.POST.get("new_password")
            repeat_new_password = request.POST.get("repeat_new_password")
            if new_password != repeat_new_password:
                return JsonResponse(
                    {"status": False, "message": _("Пароли не совпадают")}
                )

            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

            return JsonResponse({"status": True})


class AccountFullPasswordUpdateView(View):
    def post(self, request):
        email = request.POST.get("email")
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": _("Запрашиваемый пользователь не найден")}
            )

        uidb64 = urlsafe_base64_encode(force_bytes(user.id))

        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        token = jwt.encode(
            {"email": email, "exp": expiration}, settings.SECRET_KEY, algorithm="HS256"
        )

        reset_url = "https://hermesinternational.ru" + reverse(
            "accounts:password_reset_confirm", args=[uidb64, token]
        )

        current_site = get_current_site(request)
        subject = _("Сброс пароля")
        message = render_to_string(
            "accounts/email/password_reset_request.html",
            {"user": user, "reset_url": reset_url, "domain": current_site.domain},
        )
        send_email(body=message, subject=subject, recipients=[email])

        return JsonResponse(
            {
                "status": True,
                "message": _("Ссылка для сброса пароля успешно отправлена"),
            }
        )


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


def get_warehouse_options(request):
    warehouse_options = []

    warehouses = Warehouse.objects.all()
    for warehouse in warehouses:
        warehouse_options.append(
            {
                "value": warehouse.id,
                "label": _("Наш склад: ")
                + f"{warehouse.state}, {warehouse.city}, {warehouse.address}",
                "model": "Warehouse",
            }
        )

    account_warehouses = AccountWarehouse.objects.filter(account=request.user).all()
    for account_warehouse in account_warehouses:
        warehouse_options.append(
            {
                "value": account_warehouse.id,
                "label": _("Ваш склад: ")
                + f"{account_warehouse.state}, {account_warehouse.city}, {account_warehouse.address}",
                "model": "AccountWarehouse",
            }
        )

    return warehouse_options


class AccountWarehouseListView(LoginRequiredMixin, View):
    def get(self, request):
        warehouse_options = get_warehouse_options(request)
        return JsonResponse({"status": True, "warehouse_options": warehouse_options})


class AccountAvatarChange(View):
    def post(self, request):
        if request.FILES.get("profile_image"):
            user = request.user
            profile_image = request.FILES["profile_image"]
            user.profile_image = profile_image
            user.save()
            return JsonResponse({"image_url": user.profile_image.url})
        return JsonResponse({"error": "Image upload failed"}, status=400)
    

class GetPurchasePhoto(View):
    def post(self, request):
        request_data = request.POST
        purchase_id = request_data.get("purchaseId")

        purchase = Purchase.objects.get(id=int(purchase_id))
        photos = purchase.get_purchase_photos()
        response = {
            "status": 200,
            "purchase": model_to_dict(purchase),
            "photos": [{'url': photo.photo.url, "id": photo.id} for photo in photos]
        }

        return JsonResponse(response)


class PurchasePhotoDelete(View):
    def post(self, request):
        request_data = request.POST
        purchase_id = request_data.get("photoId")

        PurchasePhoto.objects.get(id=purchase_id).delete()
        return JsonResponse({"status": 200})
    

class PurchasePhotoAdd(View):
    def post(self, request):
        request_data = request.POST
        purchase_id = request_data.get("purchaseId")
        files = request.FILES.getlist('file') 

        for file in files:
            with open(os.path.join('media/purchase_photos', file.name), 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
                    PurchasePhoto.objects.create(
                        purchase=Purchase.objects.get(id=int(purchase_id)),
                        photo=f"purchase_photos/{file.name}"
                    )

        return GetPurchasePhoto.post(self, request)