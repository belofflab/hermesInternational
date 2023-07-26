from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View

from .models import Invoice
from .services.crypto import Crypto

crypto = Crypto(token=settings.CRYPTO_BOT_TOKEN)


class InvoiceView(View):
    def post(self, request):
        payload = request.POST.get("payload")
        invoice = Invoice.objects.get(invoice_id=payload["invoice_id"])
        if payload["status"] == "paid":
            invoice.status = "paid"
            invoice.save()
        if payload["status"] == "expired":
            invoice.status = "expired"
            invoice.save()


class InvoiceCreateView(View):
    def get(self, request):
        return render(request, "payments/create_invoice.html", context={})

    def post(self, request):
        created_invoice = crypto.createInvoice(
            "USDT", amount=request.POST.get("amount")
        )
        if created_invoice.get("ok"):
            result = created_invoice.get("result")
            new_invoice = Invoice.objects.create(
                account=request.user,
                invoice_id=result["invoice_id"],
                asset=result["asset"],
                amount=result["amount"],
                pay_url=result["pay_url"],
                status=result["status"],
                created_at=result["created_at"],
            )
            return render(
                request,
                "payments/create_invoice.html",
                context={"new_invoice": new_invoice},
            )
        return render(
            request,
            "payments/create_invoice.html",
            context={
                "error": "Ошибка создания ссылки на оплату... Обратитесь в поддержку"
            },
        )
