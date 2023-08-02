from django.urls import path

from .views import InvoiceView, InvoiceDetailView

app_name="payments"
urlpatterns = [
    path("invoice/Y7ACEnFxgk5XHXltIBDPiEBeL9V79nTX", InvoiceView.as_view(), name="invoice"),
    path('invoices/<slug:invoice_slug>/', InvoiceDetailView.as_view(), name='invoice_detail'),
]