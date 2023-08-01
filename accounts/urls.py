from django.urls import path

from . import views
app_name = 'accounts'
urlpatterns = [
  path('logout/', views.LogoutView.as_view(), name='logout'),
  path('profile/', views.ProfileView.as_view(), name='profile'),
  path('profile/warehouses/', views.ProfileWarehouseView.as_view(), name='warehouses'),
  path('profile/simple_purchase/', views.ProfileSimplePurchaseView.as_view(), name='simple_purchase'),
  path('profile/payment/', views.ProfilePaymentView.as_view(), name='payment'),
  path('profile/packages/', views.ProfilePackagesView.as_view(), name='packages'),
  path('profile/inbox/', views.InboxView.as_view(), name="inbox"),
  path('profile/buyout/', views.BuyOutView.as_view(), name="buyout"),
  path('profile/inbox/<int:pk>/', views.PurchaseDetailView.as_view(), name="inbox_detail"),
  path('profile/reset-password/', views.ResetPasswordView.as_view(), name='reset_password')
]
