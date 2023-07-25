from django.urls import path

from .views import InvoiceView, InvoiceCreateView

app_name="payments"
urlpatterns = [
    path("invoice/", InvoiceView.as_view(), name="invoice"),
    path("invoice/create/", InvoiceCreateView.as_view(), name="invoice")
]