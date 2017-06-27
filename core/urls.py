from django.conf.urls import url

from core.views import general
from core.views import certificates
from core.views import root_crt
from core.views import rest

urlpatterns = [
    url(r'^$', general.Index.as_view(), name='index'),
    url(r'^certificates/$', certificates.Search.as_view(), name='certificates_search'),
    url(r'^certificates/create/$', certificates.Create.as_view(), name='certificates_create'),
    url(r'^certificates/upload_existing/$', certificates.UploadExisting.as_view(), name='certificates_upload_existing'),
    url(r'^certificates/(?P<pk>[0-9]+)/$', certificates.View.as_view(), name='certificates_view'),
    url(r'^certificates/(?P<pk>[0-9]+)/recreate/$', certificates.Recreate.as_view(), name='certificates_recreate'),
    url(r'^certificates/(?P<pk>[0-9]+)/delete/$', certificates.Delete.as_view(), name='certificates_delete'),
    url(r'^certificates/(?P<pk>[0-9]+)/download_crt/$', certificates.DownloadCrt.as_view(), name='certificates_download_crt'),
    url(r'^certificates/(?P<pk>[0-9]+)/download_key/$', certificates.DownloadKey.as_view(), name='certificates_download_key'),

    url(r'^root_crt/$', root_crt.CrtChoice.as_view(), name='root_crt'),
    url(r'^root_crt/already_exists/$', root_crt.Exists.as_view(), name='root_crt_exists'),
    url(r'^root_crt/upload_existing/$', root_crt.UploadExisting.as_view(), name='root_crt_upload_existing'),
    url(r'^root_crt/generate_new/$', root_crt.GenerateNew.as_view(), name='root_crt_generate_new'),
    url(r'^root_crt/view/$', root_crt.View.as_view(), name='root_crt_view'),
    url(r'^root_crt/recreate/$', root_crt.Recreate.as_view(), name='root_crt_recreate'),
    url(r'^root_crt/delete/$', root_crt.Delete.as_view(), name='root_crt_delete'),
    url(r'^root_crt/download_crt/$', root_crt.DownloadRootCrt.as_view(), name='root_crt_download'),

    url(r'^api/site_crt/create/$', rest.SiteCrtCreate.as_view(), name='rest_site_crt_create'),
    url(r'^api/site_crt/$', rest.SiteCrtList.as_view(), name='rest_site_crt_list'),
]
