from modeltranslation.translator import translator, TranslationOptions


from .models import PurchaseDeliveryOption



class PurchaseDeliveryOptionTranslationOptions(TranslationOptions):
    fields = ('name', )


translator.register(PurchaseDeliveryOption, PurchaseDeliveryOptionTranslationOptions    )