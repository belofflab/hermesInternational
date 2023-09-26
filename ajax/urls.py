from django.urls import path

from . import views

app_name = "ajax"
urlpatterns = [
    path("inbox/create", views.PurchaseCreateView.as_view(), name="inbox_detail"),
    path(
        "account/data/create",
        views.AccountDataCreateView.as_view(),
        name="account_data_create",
    ),
    path(
        "account/data/update",
        views.AccountDataUpdateView.as_view(),
        name="account_data_update",
    ),
    path(
        "account/password/update",
        views.AccountPasswordUpdateView.as_view(),
        name="account_password_update",
    ),
    path(
        "account/full_password/update",
        views.AccountFullPasswordUpdateView.as_view(),
        name="account_full_password_update",
    ),
    path(
        "accounts/profile/warehouses/create",
        views.AccountWarehouseCreateView.as_view(),
        name="warehouse_create",
    ),
    path(
        "accounts/profile/warehouses/delete",
        views.AccountWarehouseDeleteView.as_view(),
        name="warehouse_delete",
    ),
    path(
        "accounts/profile/warehouses/all",
        views.AccountWarehouseListView.as_view(),
        name="warehouse_list",
    ),
    path(
        "accounts/profile/purchases/get",
        views.PurchaseGetView.as_view(),
        name="purchase_get",
    ),
    path(
        "accounts/profile/purchases/remove",
        views.PurchaseRemoveView.as_view(),
        name="purchase_remove",
    ),
    path(
        "accounts/profile/purchases/pay",
        views.PurchasePayView.as_view(),
        name="purchase_pay",
    ),
    path(
        "accounts/profile/purchases/status/update",
        views.PurchaseUpdateStatusView.as_view(),
        name="purchase_status_update",
    ),
    path("accounts/login", views.LoginView.as_view(), name="login"),
    path("accounts/signup", views.RegistrationView.as_view(), name="signup"),
    path("accounts/profile", views.AccountNotifySettingsView.as_view(), name="profile"),
    path(
        "accounts/profile/avatar",
        views.AccountAvatarChange.as_view(),
        name="profile_avatar",
    ),
    path(
        "purchase/status/update",
        views.PurchaseChangeStatusView.as_view(),
        name="purchase_change_status",
    ),
]
