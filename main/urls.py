from django.urls import path

from . import views

app_name="main"
urlpatterns = [
    path('', views.index, name="index"),
    path('pricing/', views.pricing, name="pricing"),
    path('about/', views.about, name="about"),
    path('reviews/', views.reviews, name="reviews")
]