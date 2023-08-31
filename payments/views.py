import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from accounts.models import Account
from .models import Invoice
from .services.crypto import Crypto
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

crypto = Crypto(token=settings.CRYPTO_BOT_TOKEN)


@method_decorator(csrf_exempt, name="dispatch")
class InvoiceView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            payload = payload.get("payload")
            print(payload)

            invoice = Invoice.objects.get(invoice_id=payload["invoice_id"])
            invoice.status = payload["status"]

            account = Account.objects.get(email=invoice.account)
            account.update_balance(invoice.amount)
        except Exception as e:
            print("Error:", e)

        return HttpResponse(status=200)


class InvoiceDetailView(LoginRequiredMixin, View):
    def get(self, request, invoice_slug: str):
        try:
            invoice = Invoice.objects.get(slug=invoice_slug)
        except Invoice.DoesNotExist:
            return redirect("accounts:profile")
        return render(request, "payments/pay.html", context={"invoice": invoice})
