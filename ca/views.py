import os
from OpenSSL import crypto

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView, DetailView, DeleteView, ListView
from django.views.generic.edit import FormMixin

from ca.utils import CA
from ca import forms
from ca import models


class CertRootExistMixin:
    def get(self, request, *args, **kwargs):
        if models.RootCrt.objects.exists():
            return HttpResponseRedirect(reverse_lazy('root_crt_exists'))
        return super().get(request, *args, **kwargs)


class CertRootNotExistMixin:
    def get(self, request, *args, **kwargs):
        if models.RootCrt.objects.all().count() == 0:
            return HttpResponseRedirect(reverse_lazy('root_crt_not_exists'))
        return super().get(request, *args, **kwargs)


class CrtExist(TemplateView):
    template_name = 'ca/root_crt_managing/root_already_exists.html'


class CrtNotExist(TemplateView):
    template_name = 'ca/root_crt_managing/root_not_exists.html'


class IndexRootCrt(CertRootExistMixin, TemplateView):
    template_name = 'ca/root_crt_managing/index.html'


class LoadRootCrt(CertRootExistMixin, CreateView):
    form_class = forms.RootCrt
    template_name = 'ca/root_crt_managing/has_root_key.html'
    success_url = reverse_lazy('view_root_crt')


class ViewRootCrt(DetailView):
    model = models.RootCrt
    template_name = 'ca/root_crt_managing/view_root_crt.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)

    def get_context_data(self, **kwargs):
        with open(self.object.crt.path, 'rt') as cert:
            cert_data = cert.read().encode()
            kwargs['cert'] = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data).get_subject()
        return super().get_context_data(**kwargs)


class RootCrtDelete(DeleteView):
    model = models.RootCrt
    template_name = 'ca/root_crt_managing/delete_root.html'
    success_url = reverse_lazy('index_root')

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)

    def delete(self, request, *args, **kwargs):
        path_root_dir = os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH)
        directory = os.listdir(path_root_dir)
        for file in directory:
            os.remove(os.path.join(path_root_dir, file))
        return super().delete(request, *args, **kwargs)


class GenerateRootCrt(CertRootExistMixin, FormView):
    form_class = forms.ConfigRootCrt
    template_name = 'ca/root_crt_managing/no_root_key.html'
    success_url = reverse_lazy('view_root_crt')

    def form_valid(self, form):
        ca = CA()
        ca.generate_root_certificate(form.cleaned_data)
        return super(GenerateRootCrt, self).form_valid(form)


class SearchSiteCrt(CertRootNotExistMixin, FormMixin, ListView):
    form_class = forms.SearchSiteCrt
    model = models.SiteCrt
    template_name = 'ca/index.html'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')
        form = self.form_class(self.request.GET)
        if form.is_valid():
            cn = form.cleaned_data['cn']
            if cn:
                queryset = queryset.filter(cn=cn)
        return queryset

    def get_context_data(self, **kwargs):
        kwargs['object'] = models.RootCrt.objects.first()
        return super().get_context_data(**kwargs)


class CreateSiteCrt(CertRootNotExistMixin, FormView):
    form_class = forms.CreateSiteCrt
    success_url = reverse_lazy('index')
    template_name = 'ca/create_crt.html'

    def form_valid(self, form):
        ca = CA()
        ca.generate_site_certificate(form.cleaned_data['cn'])
        return super().form_valid(form)


def upload_existing(request):
    return render(request, 'ca/upload_existing.html')


def view_crt(request):
    return render(request, 'ca/view_crt.html')
