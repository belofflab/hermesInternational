from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/admin/", views.ProfileAdminView.as_view(), name="profile_admin"),
    path(
        "profile/password/reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "profile/warehouses/", views.ProfileWarehouseView.as_view(), name="warehouses"
    ),
    path(
        "profile/simple_purchase/",
        views.ProfileSimplePurchaseView.as_view(),
        name="simple_purchase",
    ),
    path("profile/payment/", views.ProfilePaymentView.as_view(), name="payment"),
    path("profile/prices/", views.ProfilePricesView.as_view(), name="prices"),
    path("profile/packages/", views.ProfilePackagesView.as_view(), name="packages"),
    path("profile/inbox/", views.InboxView.as_view(), name="inbox"),
    path("profile/buyout/", views.BuyOutView.as_view(), name="buyout"),
    path("profile/mail/", views.MailListView.as_view(), name="mail_list"),
    path("profile/mail/send/", views.MailSendView.as_view(), name="send_email"),
    path(
        "profile/inbox/<int:pk>/",
        views.PurchaseDetailView.as_view(),
        name="inbox_detail",
    ),
]
