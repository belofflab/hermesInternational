from django.urls import path

from . import views
app_name = 'ajax'
urlpatterns = [
  path('inbox/create', views.PurchaseCreateView.as_view(), name="inbox_detail"),

  path('account/data/create', views.AccountDataCreateView.as_view(), name="account_data_create"),
  path('account/data/update', views.AccountDataUpdateView.as_view(), name="account_data_update"),
  
  path('accounts/profile/warehouses/create', views.AccountWarehouseCreateView.as_view(), name='warehouse_create'),
  path('accounts/profile/warehouses/delete', views.AccountWarehouseDeleteView.as_view(), name='warehouse_delete'),

  path('accounts/profile/purchases/get', views.PurchaseGetView.as_view(), name='purchase_get'),
  path('accounts/profile/purchases/remove', views.PurchaseRemoveView.as_view(), name='purchase_remove'),


  path('accounts/login', views.LoginView.as_view(), name="login"),
  path('accounts/signup', views.RegistrationView.as_view(), name="signup"),
  path('accounts/profile', views.AccountNotifySettingsView.as_view(), name='profile'),
  path('accounts/profile/avatar', views.AccountAvatarChange.as_view(), name='profile_avatar'),

  path('purchase/status/update', views.PurchaseChangeStatusView.as_view(), name="purchase_change_status")
]
