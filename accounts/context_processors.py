
from accounts.models import PurchaseDeliveryOption, Account
def delivery_options(request):
    return {"delivery_options": PurchaseDeliveryOption.objects.filter(is_visible=True).all()}


def account_information(request):
    return {"account_information": Account.objects.get(email=request.user)}