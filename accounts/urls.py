from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views
app_name = 'accounts'
urlpatterns = [
  path('login/', views.LoginView.as_view(), name='login'),
  path('signup/', views.RegistrationView.as_view(), name='signup'),
  path('logout/', LogoutView.as_view(next_page="/"), name='logout'),
  path('profile/', views.ProfileView.as_view(), name='profile'),
  path('profile/warehouses/', views.ProfileWarehouseView.as_view(), name='warehouses'),
  path('profile/collect-parcel/', views.CollectParcelView.as_view(), name='collect_parcel'),
  path('profile/payment/', views.ProfilePaymentView.as_view(), name='payment'),
  path('profile/packages/', views.ProfilePackagesView.as_view(), name='packages'),
  path('profile/outbox/', views.ProfileOutboxView.as_view(), name='outbox'),
  path('profile/inbox/', views.InboxView.as_view(), name="inbox"),
  path('profile/inbox/<int:pk>/', views.PurchaseDetailView.as_view(), name="inbox_detail"),
  path('profile/reset-password/', views.ResetPasswordView.as_view(), name='reset_password')
]
