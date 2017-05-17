import os
from OpenSSL import crypto

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView, DetailView, DeleteView

from ca.utils import create_self_signed_cert_root
from ca import forms
from ca import models


class CertExistMixin:
    def get(self, request, *args, **kwargs):
        if models.RootCrt.objects.exists():
            return HttpResponseRedirect(reverse_lazy('root_crt_exist'))
        return super().get(request, *args, **kwargs)


class CrtExist(TemplateView):
    template_name = 'ca/root_already_exists.html'


class IndexRootCrt(CertExistMixin, TemplateView):
    template_name = 'ca/index.html'


class LoadRootCrt(CertExistMixin, CreateView):
    form_class = forms.RootCrt
    template_name = 'ca/has_root_key.html'
    success_url = reverse_lazy('view_root_crt')


class ViewRootCrt(DetailView):
    model = models.RootCrt
    template_name = 'ca/view_root_crt.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)

    def get_context_data(self, **kwargs):
        context = super(ViewRootCrt, self).get_context_data(**kwargs)

        cert_path = os.path.join(settings.MEDIA_ROOT, str(models.RootCrt.objects.first().crt))
        st_cert = open(cert_path, 'rt').read()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, st_cert)

        context['C'] = cert.get_subject()
        return context


class RootCrtDelete(DeleteView):
    model = models.RootCrt
    template_name = 'ca/delete_root.html'
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        directory = os.listdir(settings.ROOT_CA)
        for file in directory:
            os.remove(os.path.join(settings.ROOT_CA, file))
        return HttpResponseRedirect(self.success_url)


class GenerateRootCrt(CertExistMixin, FormView):
    form_class = forms.ConfigRootCrt
    template_name = 'ca/no_root_key.html'
    success_url = reverse_lazy('view_root_crt')

    def form_valid(self, form):
        create_self_signed_cert_root(form.cleaned_data)
        return super(GenerateRootCrt, self).form_valid(form)
