import os
from datetime import datetime
from OpenSSL import crypto

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
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


class AjaxCopyDataCertMixin:
    def render_to_json_response(self):
        return JsonResponse(self.get_data())

    def get_data(self):
        if self.request.GET.get('pk'):
            pk = int(self.request.GET.get('pk'))
            crt = models.SiteCrt.objects.get(pk=pk)
            crt_data = crt.crt.read().decode()
            key_data = crt.key.read().decode()

            ajax_response = {'crt': crt_data, 'key': key_data}

            return ajax_response

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            return self.render_to_json_response()
        else:
            return super().render_to_response(context, **response_kwargs)


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


class SearchSiteCrt(FormMixin, ListView):
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
        kwargs['object'] = models.RootCrt.objects.get()
        return super().get_context_data(**kwargs)


class CreateSiteCrt(CertRootNotExistMixin, FormView):
    form_class = forms.CreateSiteCrt
    success_url = reverse_lazy('index')
    template_name = 'ca/create_crt.html'

    def form_valid(self, form):
        ca = CA()
        ca.generate_site_certificate(form.cleaned_data['cn'], form.cleaned_data['validity_period'])
        return super().form_valid(form)


class LoadSiteCrt(CertRootNotExistMixin, FormView):
    template_name = 'ca/upload_existing.html'
    form_class = forms.SiteCrt
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        if form.cleaned_data['crt_file']:
            crt_file_data = form.cleaned_data['crt_file'].read()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, crt_file_data)
            models.SiteCrt.objects.create(
                key=form.cleaned_data['key_file'],
                crt=form.cleaned_data['crt_file'],
                cn=cert.get_subject().CN,
                date_end=datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
            )
        elif form.cleaned_data['crt_text']:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, form.cleaned_data['crt_text'])
            cn = cert.get_subject().CN
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, form.cleaned_data['key_text'])
            CA.write_cert_site(cert, pkey, cn)
            models.SiteCrt.objects.create(
                key=os.path.join(cn, cn + '.key'),
                crt=os.path.join(cn, cn + '.crt'),
                cn=cn,
                date_end=datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
            )
        return super().form_valid(form)


class ViewSiteCrt(AjaxCopyDataCertMixin, DetailView):
    template_name = 'ca/view_crt.html'
    model = models.SiteCrt

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        with open(self.object.crt.path, 'rt') as cert:
            cert_data = cert.read().encode()
            kwargs['cert'] = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data).get_subject()
        return super().get_context_data(**kwargs)


class SiteCrtDelete(CertRootNotExistMixin, DeleteView):
    model = models.SiteCrt
    template_name = 'ca/delete_crt.html'
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        path_root_dir = os.path.join(settings.MEDIA_ROOT, os.path.dirname(self.get_object().crt.name))
        directory = os.listdir(path_root_dir)
        for file in directory:
            os.remove(os.path.join(path_root_dir, file))
        return super().delete(request, *args, **kwargs)


class RecreationSiteCrt(FormView):
    form_class = forms.RecreationSiteCrt
    template_name = 'ca/recreation_crt.html'

    def get_success_url(self):
        return reverse_lazy('view_crt', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = models.SiteCrt.objects.get(pk=self.kwargs['pk'])
        path_root_dir = os.path.join(settings.MEDIA_ROOT, os.path.dirname(self.object.crt.name))
        directory = os.listdir(path_root_dir)
        for file in directory:
            os.remove(os.path.join(path_root_dir, file))
        ca = CA()
        ca.generate_site_certificate(self.object.cn, form.cleaned_data['validity_period'], pk=self.object.pk)
        messages.success(self.request, 'Recreation success')
        return super().form_valid(form)
