import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.db.models import Q

from django.views import View

from . import forms, models

from main.models import Warehouse


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class ProfileView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def get(self, request):
        context = {
            'warehouses': Warehouse.objects.all()
        }
        return render(request, "accounts/profile.html", context)

    def post(self, request):
        return render(request, "accounts/profile.html", {})


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/accounts/profile/")

        form = forms.LoginForm(request.POST or None)

        context = {"form": form, "title": "Sign In"}
        return render(request, "accounts/login.html", context)

    def post(self, request, *args, **kwargs):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                login(request=request, user=user)
                models.Visits.objects.update_or_create(
                    account=user,
                    last_login=datetime.datetime.now(),
                    ip=get_client_ip(request),
                )
                return redirect("/accounts/profile/")

        context = {"form": form, "title": "Sign Up"}
        return render(request, "accounts/login.html", context)


class RegistrationView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/accounts/profile/")
        form = forms.RegistrationForm(request.POST or None)
        context = {"form": form, "title": "Sign Up"}

        return render(request, "accounts/signup.html", context)

    def post(self, request):
        form = forms.RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.email = form.cleaned_data["email"]
            new_user.first_name = form.cleaned_data["first_name"]
            new_user.last_name = form.cleaned_data["last_name"]
            new_user.save()
            new_user.set_password(form.cleaned_data["password"])
            new_user.save()
            user = authenticate(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            login(request=request, user=user)
            models.Visits.objects.update_or_create(
                    account=user,
                    last_login=datetime.datetime.now(),
                    ip=get_client_ip(request),
                )
            return redirect("/accounts/profile/")

        context = {"form": form, "title": "Sign Up"}

        return render(request, "accounts/signup.html", context)



class CollectParcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        return render(request, "accounts/collect_parcel.html", {})
    
class ProfileOutboxView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        return render(request, "accounts/outbox.html", {})

class ResetPasswordView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = forms.ResetPasswordForm(request.POST or None)

        context = {"form": form, "title": "res"}
        return render(request, "accounts/reset-password.html", context)

    def post(self, request, *args, **kwargs):
        form = forms.ResetPasswordForm(request.POST)
        if form.is_valid():
            user = models.Account.objects.get(username=request.user)
            new_password = form.cleaned_data["new_password"]
            user.set_password(new_password)
            user.save()
            return redirect("/accounts/logout/")

        context = {"form": form, "title": "Sign Up"}
        return render(request, "accounts/reset-password.html", context)
