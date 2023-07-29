from django.views import View
from django.http.response import JsonResponse

from accounts.models import Purchase, Account, AccountData
from django.contrib.auth.mixins import LoginRequiredMixin



class PurchaseCreateView(LoginRequiredMixin, View):
    def post(self, request):
        print(request.user)
        request_data = request.POST
        name = request_data.get("name")
        url = request_data.get("url")
        track_number = request_data.get("track_number")
        quantity = request_data.get("quantity")
        price = request_data.get("price")
        status = request_data.get("status")

        new_purchase = Purchase.objects.create(
            name=name,
            link=url,
            quantity=quantity,
            price=price,
            tracking_number=track_number,
            status=status
        )

        current_user = Account.objects.get(email=request.user)

        current_user.purchases.add(new_purchase)
        
        return JsonResponse({"status": True, "data": new_purchase.id})
    
class AccountDataCreateView(LoginRequiredMixin, View):
    def post(self, request):
        request_data = request.POST
        phone = request_data.get("phone")
        city = request_data.get("city")
        street = request_data.get("street")
        state = request_data.get("state")
        postal_code = request_data.get("postal_code")
        country = request_data.get("country")

        purchase = Purchase.objects.get(id=request_data.get("purchase"))

        new_account = AccountData.objects.create(
            phone=phone,
            city=city,
            street=street,
            state=state,
            postal_code=postal_code,
            country=country
        )

        purchase.address = new_account

        purchase.save()

        return JsonResponse({"status": True, "message":""})
