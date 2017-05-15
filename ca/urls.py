from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^has_root_key/$', views.has_root_key, name='has_root_key'),
    url(r'^no_root_key/$', views.no_root_key, name='no_root_key'),
]
