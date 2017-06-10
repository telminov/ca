from django.conf.urls import url

from core import views
from core import rest

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),

    url(r'^certificates/$', views.CertificatesSearch.as_view(), name='certificates_search'),
    url(r'^certificates/create/$', views.CertificatesCreate.as_view(), name='certificates_create'),
    url(r'^certificates/upload_existing/$', views.CertificatesUploadExisting.as_view(), name='certificates_upload_existing'),
    url(r'^certificates/(?P<pk>[0-9]+)/$', views.CertificatesView.as_view(), name='certificates_view'),
    url(r'^certificates/(?P<pk>[0-9]+)/recreate/$', views.CertificatesRecreate.as_view(), name='certificates_recreate'),
    url(r'^certificates/(?P<pk>[0-9]+)/delete/$', views.CertificatesDelete.as_view(), name='certificates_delete'),

    url(r'^root_crt/$', views.RootCrt.as_view(), name='root_crt'),
    url(r'^root_crt/already_exists/$', views.RootCrtExists.as_view(), name='root_crt_exists'),
    url(r'^root_crt/upload_existing/$', views.RootCrtUploadExisting.as_view(), name='root_crt_upload_existing'),
    url(r'^root_crt/generate_new/$', views.RootCrtGenerateNew.as_view(), name='root_crt_generate_new'),
    url(r'^root_crt/view/$', views.RootCrtView.as_view(), name='root_crt_view'),
    url(r'^root_crt/recreate/$', views.RootCrtRecreate.as_view(), name='root_crt_recreate'),
    url(r'^root_crt/delete/$', views.RootCrtDelete.as_view(), name='root_crt_delete'),

    url(r'^api/site_crt/create/$', rest.SiteCrtCreate.as_view(), name='rest_site_crt_create'),
    url(r'^api/site_crt/$', rest.SiteCrtList.as_view(), name='rest_site_crt_list'),
]
