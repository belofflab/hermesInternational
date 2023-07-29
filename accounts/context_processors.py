
from accounts.models import PurchaseDeliveryOption
def delivery_options(request):
    return {"delivery_options": PurchaseDeliveryOption.objects.filter(is_visible=True).all()}