from django.urls import path

from . import views

app_name="main"
urlpatterns = [
    path('', views.index, name="index"),
    path('shops/', views.shops, name="shops"),
    path("email_test/", views.email_test, name="email_test")
],