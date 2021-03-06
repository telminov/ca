from datetime import datetime, timedelta

from OpenSSL import crypto
from djutils.views.generic import SortMixin

from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, DetailView, DeleteView, ListView
from django.views.generic.edit import FormMixin, ContextMixin

from core.utils import Ca
from core import forms
from core import models


class BreadcrumbsMixin(ContextMixin):
    def get_breadcrumbs(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class Search(BreadcrumbsMixin, SortMixin, FormMixin, ListView):
    form_class = forms.CertificatesSearch
    model = models.SiteCrt
    template_name = 'core/certificate/search.html'
    sort_params = ['cn', 'date_start', 'date_end']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            cn = form.cleaned_data['cn']
            if cn:
                queryset = queryset.filter(cn__icontains=cn)
        return queryset


class Create(BreadcrumbsMixin, FormView):
    form_class = forms.CertificatesCreate
    template_name = 'core/certificate/create.html'

    def get_success_url(self):
        return reverse_lazy('certificates_view', kwargs={'pk': self.object.pk})

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('Create new certificate', '')
        )

    def get_initial(self):
        return {'validity_period': timezone.now() + timedelta(days=settings.VALIDITY_PERIOD_CRT)}

    def form_valid(self, form):
        ca = Ca()
        if ca.get_type_alt_names(form.cleaned_data['cn']):
            self.object = ca.generate_site_crt(form.cleaned_data['cn'], form.cleaned_data['validity_period'], alt_name='IP')
        else:
            self.object = ca.generate_site_crt(form.cleaned_data['cn'], form.cleaned_data['validity_period'])
        return super().form_valid(form)


class UploadExisting(BreadcrumbsMixin, FormView):
    template_name = 'core/certificate/upload_existing.html'
    form_class = forms.CertificatesUploadExisting
    success_url = reverse_lazy('certificates_search')

    def get_success_url(self):
        return reverse_lazy('certificates_view', kwargs={'pk': self.object.pk})

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('Load an existing certificate', '')
        )

    def form_valid(self, form):
        current_tz = timezone.get_current_timezone()
        if form.cleaned_data['crt_file']:
            crt_file_data = form.cleaned_data['crt_file'].read().decode()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, crt_file_data)
            self.object = models.SiteCrt.objects.create(
                key=form.cleaned_data['key_file'].read().decode(),
                crt=crt_file_data,
                cn=cert.get_subject().CN,
                date_end=current_tz.localize(datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ'))
            )
        elif form.cleaned_data['crt_text']:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, form.cleaned_data['crt_text'])
            cn = cert.get_subject().CN
            self.object = models.SiteCrt.objects.create(
                key=form.cleaned_data['key_text'],
                crt=form.cleaned_data['crt_text'],
                cn=cn,
                date_end=current_tz.localize(datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ'))
            )
        return super().form_valid(form)


class View(BreadcrumbsMixin, FormMixin, DetailView):
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
        crt_data = crt.crt
        key_data = crt.key
        return {'crt': crt_data, 'key': key_data}

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        cert_data = self.object.crt.encode()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
        kwargs['cert'] = cert.get_subject()
        kwargs['crt_validity_period'] = datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
        return super().get_context_data(**kwargs)


class Delete(BreadcrumbsMixin, DeleteView):
    model = models.SiteCrt
    template_name = 'core/certificate/delete.html'
    success_url = reverse_lazy('certificates_search')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View %s' % self.get_object().cn, reverse('certificates_view', kwargs={'pk': self.kwargs['pk']})),
            ('Delete %s' % self.get_object().cn, '')
        )

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


class Recreate(BreadcrumbsMixin, FormView, DetailView):
    model = models.SiteCrt
    form_class = forms.RecreationCrt
    template_name = 'core/certificate/recreate.html'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View %s' % models.SiteCrt.objects.get(pk=self.kwargs['pk']).cn,
             reverse('certificates_view', kwargs={'pk': self.kwargs['pk']})),
            ('Recreate certificate', '')
        )

    def get_success_url(self):
        return reverse_lazy('certificates_view', kwargs={'pk': self.kwargs['pk']})

    def get_initial(self):
        return {'validity_period': timezone.now() + timedelta(days=settings.VALIDITY_PERIOD_CRT)}

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = models.SiteCrt.objects.get(pk=self.kwargs['pk'])
        ca = Ca()
        ca.generate_site_crt(self.object.cn, form.cleaned_data['validity_period'], self.kwargs['pk'])
        messages.success(self.request, 'Recreation success')
        return super().form_valid(form)


class DownloadCrt(View):

    def get(self, context, **response_kwargs):
        pk = self.kwargs['pk']
        obj = models.SiteCrt.objects.get(pk=pk)
        res = HttpResponse(obj.crt, content_type='application/txt')
        res['Content-Disposition'] = 'attachment; filename={}.crt'.format(obj.cn)
        return res


class DownloadKey(View):
    def get(self, context, **response_kwargs):
        pk = self.kwargs['pk']
        obj = models.SiteCrt.objects.get(pk=pk)
        res = HttpResponse(obj.key, content_type='application/txt')
        res['Content-Disposition'] = 'attachment; filename={}.key'.format(obj.cn)
        return res
