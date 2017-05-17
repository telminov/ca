from django.contrib.auth.views import login, logout_then_login
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

from ca import models

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', login, {'template_name': 'ca/login_page.html', 'redirect_authenticated_user': True,
                            'extra_context': {'object': models.RootCrt.objects.first()}}, name='login'),
    url(r'^logout/', logout_then_login, {'login_url': '/login/?next=/'}, name='logout'),
    url(r'^', include('ca.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
