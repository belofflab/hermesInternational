from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("payments/", include("payments.urls")),
    path('i18n/', include('django.conf.urls.i18n'))
]

urlpatterns += i18n_patterns(
    path('', include('main.urls'), name="main"),
    path('accounts/', include('accounts.urls'), name="accounts")
) 

urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# handler404='trading.views.handler404'
# handler403='trading.views.handler403'
# handler500='trading.views.handler500'