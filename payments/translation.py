from modeltranslation.translator import translator, TranslationOptions


from .models import Service


class ServiceOptionTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Service, ServiceOptionTranslationOptions)
