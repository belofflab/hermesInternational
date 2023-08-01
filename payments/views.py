from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
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
    
class InvoiceDetailView(LoginRequiredMixin, View):
    def get(self, request, invoice_slug: str):
        try:
            invoice = Invoice.objects.get(slug=invoice_slug)
        except Invoice.DoesNotExist:
            return redirect("accounts:profile")
        return render(request, "payments/pay.html", context={"invoice": invoice})
