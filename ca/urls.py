from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^change_root_crt/$', views.IndexRootCrt.as_view(), name='index_root'),
    url(r'^has_root_key/$', views.LoadRootCrt.as_view(), name='has_root_key'),
    url(r'^view_root_crt/$', views.ViewRootCrt.as_view(), name='view_root_crt'),
    url(r'^no_root_key/$', views.GenerateRootCrt.as_view(), name='no_root_key'),
    url(r'^root_exists/$', views.CrtExist.as_view(), name='root_crt_exists'),
    url(r'^root_not_exists/$', views.CrtNotExist.as_view(), name='root_crt_not_exists'),
    url(r'^delete_root_crt/$', views.RootCrtDelete.as_view(), name='delete_root_crt'),
    url(r'^$', views.SearchSiteCrt.as_view(), name='index'),
    url(r'^create_crt/$', views.CreateSiteCrt.as_view(), name='create_crt')

]
