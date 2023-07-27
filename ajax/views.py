from django.views import View
from django.http.response import JsonResponse

from accounts.models import Purchase, Account
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
