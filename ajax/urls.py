from django.urls import path

from . import views
app_name = 'ajax'
urlpatterns = [
  path('inbox/create', views.PurchaseCreateView.as_view(), name="inbox_detail"),
  path('account/data/create', views.AccountDataCreateView.as_view(), name="address_detail"),
]
