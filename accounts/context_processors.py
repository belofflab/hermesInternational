
from accounts.models import PurchaseDeliveryOption, Account
def delivery_options(request):
    return {"delivery_options": PurchaseDeliveryOption.objects.filter(is_visible=True).all()}


def account_information(request):
    try:
        account = Account.objects.get(email=request.user)
    except:
        account = {}
    return {"account_information": account}