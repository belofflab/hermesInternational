from django.urls import path

from . import views
app_name = 'ajax'
urlpatterns = [
  path('inbox/create', views.PurchaseCreateView.as_view(), name="inbox_detail"),
]
