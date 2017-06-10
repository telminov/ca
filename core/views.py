import shutil
import os
from datetime import datetime, timedelta
from OpenSSL import crypto

from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, FormView, DetailView, DeleteView, ListView, RedirectView
from django.views.generic.edit import FormMixin, ContextMixin

from core.utils import CA
from core import forms
from core import models


class CertRootExistMixin:
    def get(self, request, *args, **kwargs):
        if models.RootCrt.objects.exists():
            return HttpResponseRedirect(reverse_lazy('root_crt_exists'))
        return super().get(request, *args, **kwargs)


class BreadcrumbsMixin(ContextMixin):
    def get_breadcrumbs(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class CrtExist(TemplateView):
    template_name = 'core/root_certificate_managing/root_already_exists.html'


class IndexRootCrt(CertRootExistMixin, TemplateView):
    template_name = 'core/root_certificate_managing/index.html'


class LoadRootCrt(BreadcrumbsMixin, CertRootExistMixin, CreateView):
    form_class = forms.RootCrt
    template_name = 'core/root_certificate_managing/has_root_key.html'
    success_url = reverse_lazy('view_root_crt')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index_root')),
            ('Load root certificate', '')
        )


class ViewRootCrt(BreadcrumbsMixin, FormMixin, DetailView):
    model = models.RootCrt
    form_class = forms.ViewCrtText
    template_name = 'core/root_certificate_managing/view_root_files.html'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View root certificate', '')
        )

    def get_initial(self):
        crt = models.RootCrt.objects.get()
        crt_data = crt.crt.read().decode()
        key_data = crt.key.read().decode()
        return {'crt': crt_data, 'key': key_data}

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)

    def get_context_data(self, **kwargs):
        with open(self.object.crt.path, 'rt') as cert:
            cert_data = cert.read().encode()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
            kwargs['cert'] = cert.get_subject()
            kwargs['crt_validity_period'] = datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
        return super().get_context_data(**kwargs)


class RootCrtDelete(BreadcrumbsMixin, DeleteView):
    model = models.RootCrt
    template_name = 'core/root_certificate_managing/delete.html'
    success_url = reverse_lazy('index_root')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View certificate', reverse('view_root_crt')),
            ('Delete root certificate', '')
        )

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)

    def delete(self, request, *args, **kwargs):
        path_root_dir = os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH)
        directory = os.listdir(path_root_dir)
        for file in directory:
            os.remove(os.path.join(path_root_dir, file))
        return super().delete(request, *args, **kwargs)


class GenerateRootCrt(BreadcrumbsMixin, CertRootExistMixin, FormView):
    form_class = forms.ConfigRootCrt
    template_name = 'core/root_certificate_managing/no_root_key.html'
    success_url = reverse_lazy('view_root_crt')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index_root')),
            ('Generate root certificate', '')
        )

    def form_valid(self, form):
        ca = CA()
        ca.generate_root_certificate(form.cleaned_data)
        return super(GenerateRootCrt, self).form_valid(form)


class Index(RedirectView):
    url = reverse_lazy('certificate_search')


class SearchSiteCrt(BreadcrumbsMixin, FormMixin, ListView):
    form_class = forms.SearchSiteCrt
    model = models.SiteCrt
    template_name = 'core/index.html'
    data_method = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')
        form = self.form_class(self.request.GET)
        if form.is_valid():
            cn = form.cleaned_data['cn']
            if cn:
                queryset = queryset.filter(cn__icontains=cn)
        return queryset


class CreateSiteCrt(BreadcrumbsMixin, FormView):
    form_class = forms.CreateSiteCrt
    success_url = reverse_lazy('certificate_search')
    template_name = 'core/certificate/create.html'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('Create new certificate', '')
        )

    def get_initial(self):
        return {'validity_period': timezone.now() + timedelta(days=settings.VALIDITY_PERIOD_CRT)}

    def form_valid(self, form):
        ca = CA()
        ca.generate_site_certificate(form.cleaned_data['cn'], form.cleaned_data['validity_period'])
        return super().form_valid(form)


class LoadSiteCrt(BreadcrumbsMixin, FormView):
    template_name = 'core/certificate/upload_existing.html'
    form_class = forms.LoadSiteCrt
    success_url = reverse_lazy('certificate_search')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('Load exists certificate', '')
        )

    def form_valid(self, form):
        current_tz = timezone.get_current_timezone()
        if form.cleaned_data['crt_file']:
            crt_file_data = form.cleaned_data['crt_file'].read()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, crt_file_data)
            models.SiteCrt.objects.create(
                key=form.cleaned_data['key_file'],
                crt=form.cleaned_data['crt_file'],
                cn=cert.get_subject().CN,
                date_end=current_tz.localize(datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ'))
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
                date_end=current_tz.localize(datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ'))
            )
        return super().form_valid(form)


class ViewSiteCrt(BreadcrumbsMixin, FormMixin, DetailView):
    template_name = 'core/certificate/view.html'
    form_class = forms.ViewCrtText
    model = models.SiteCrt

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View %s' % self.get_object().cn, '')
        )

    def get_initial(self):
        crt = models.SiteCrt.objects.get(pk=self.kwargs['pk'])
        crt_data = crt.crt.read().decode()
        key_data = crt.key.read().decode()
        return {'crt': crt_data, 'key': key_data}

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        with open(self.object.crt.path, 'rt') as cert:
            cert_data = cert.read().encode()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
            kwargs['cert'] = cert.get_subject()
            kwargs['crt_validity_period'] = datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
        return super().get_context_data(**kwargs)


class SiteCrtDelete(BreadcrumbsMixin, DeleteView):
    model = models.SiteCrt
    template_name = 'core/certificate/delete.html'
    success_url = reverse_lazy('certificate_search')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View %s' % self.get_object().cn, reverse('view_crt', kwargs={'pk': self.kwargs['pk']})),
            ('Delete %s' % self.get_object().cn, '')
        )

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        path_dir = os.path.join(settings.MEDIA_ROOT, os.path.dirname(self.get_object().crt.name))
        shutil.rmtree(path_dir)
        return super().delete(request, *args, **kwargs)


class RecreationSiteCrt(BreadcrumbsMixin, FormView, DetailView):
    model = models.SiteCrt
    form_class = forms.RecreationCrt
    template_name = 'core/certificate/recreation.html'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View %s' % models.SiteCrt.objects.get(pk=self.kwargs['pk']).cn,
             reverse('view_crt', kwargs={'pk': self.kwargs['pk']})),
            ('Recreation certificate', '')
        )

    def get_success_url(self):
        return reverse_lazy('view_crt', kwargs={'pk': self.kwargs['pk']})

    def get_initial(self):
        return {'validity_period': timezone.now() + timedelta(days=settings.VALIDITY_PERIOD_CRT)}

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

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


class RecreationRootCrt(BreadcrumbsMixin, FormView, DetailView):
    model = models.RootCrt
    form_class = forms.RecreationCrt
    template_name = 'core/certificate/recreation.html'
    success_url = reverse_lazy('view_root_crt')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View root crt', reverse('view_root_crt')),
            ('Recreation root certificate', '')
        )

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)

    def form_valid(self, form):
        self.object = models.RootCrt.objects.get()
        path_root_dir = os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH)
        directory = os.listdir(path_root_dir)
        for file in directory:
            os.remove(os.path.join(path_root_dir, file))
        ca = CA()
        ca.generate_root_certificate(form.cleaned_data, recreation=True)
        messages.success(self.request, 'Recreation success')
        return super().form_valid(form)
