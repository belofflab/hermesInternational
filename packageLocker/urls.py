from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('UQhCgbBPEuPhAbAPfwbTaX/', admin.site.urls),
    path("payments/", include("payments.urls")),
    path('ajax/', include('ajax.urls')),
    path('i18n/', include('django.conf.urls.i18n'))
]

urlpatterns += i18n_patterns(
    path('', include('main.urls'), name="main"),
    path('accounts/', include('accounts.urls'), name="accounts")
) 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# handler404='main.views.handler404'
handler403='main.views.handler403'
handler500='main.views.handler500'