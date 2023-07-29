from django.urls import path

from . import views
app_name = 'ajax'
urlpatterns = [
  path('inbox/create', views.PurchaseCreateView.as_view(), name="inbox_detail"),
  path('account/data/create', views.AccountDataCreateView.as_view(), name="address_detail"),
  path('accounts/login', views.LoginView.as_view(), name="login"),
  path('accounts/signup', views.RegistrationView.as_view(), name="signup"),
  path('accounts/profile', views.AccountNotifySettingsView.as_view(), name='profile')
]
