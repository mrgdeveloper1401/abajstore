from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from decouple import config

debug_mode = config('DEBUG', default=False, cast=bool)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('', include('products.urls')),
    path('carts/', include('carts.urls')),
    path('', include('orders.urls')),
    # path('payment/', include('payment.urls')),

]
if debug_mode:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
