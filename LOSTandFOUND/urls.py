from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import index, contact, login as signin, signup, logout_view
from item.views import report_item, retrieve_item, api_submit_claim, api_admin_claims

urlpatterns = [
    path('', index, name='index'),
    path('contact/', contact, name='contact'),
    path('login/', signin, name='login'),
    path('signin/', signin, name='signin'),
    path('signup/', signup, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('items/report/', report_item, name='report_item'),
    path('items/retrieve/', retrieve_item, name='retrieve_item'),
    path('api/claims/submit/', api_submit_claim, name='api_submit_claim'),
    path('api/admin/claims/', api_admin_claims, name='api_admin_claims'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
