from datetime import datetime

from OpenSSL import crypto

from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView, DetailView, DeleteView
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


class Exists(TemplateView):
    template_name = 'core/root_certificate_managing/already_exists.html'


class ExistsMixin:
    def get(self, request, *args, **kwargs):
        if models.RootCrt.objects.exists():
            return HttpResponseRedirect(reverse_lazy('root_crt_exists'))
        return super().get(request, *args, **kwargs)


class CrtChoice(ExistsMixin, TemplateView):
    template_name = 'core/root_certificate_managing/crt_choice.html'


class UploadExisting(BreadcrumbsMixin, ExistsMixin, FormView):
    form_class = forms.RootCrt
    template_name = 'core/root_certificate_managing/upload_existing.html'
    success_url = reverse_lazy('root_crt_view')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('root_crt')),
            ('Load root certificate', '')
        )

    def form_valid(self, form):
        obj = models.RootCrt()
        cert_data = form.cleaned_data['crt'].read()
        key_data = form.cleaned_data['key'].read()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data).get_subject()
        obj.crt = cert_data
        obj.key = key_data
        obj.country = cert.C
        obj.state = cert.ST
        obj.location = cert.L
        obj.organization = cert.O
        if cert.OU:
            obj.organizational_unit_name = cert.OU
        if cert.emailAddress:
            obj.email = cert.emailAddress

        obj.save()

        return super(UploadExisting, self).form_valid(form)


class View(BreadcrumbsMixin, FormMixin, DetailView):
    model = models.RootCrt
    form_class = forms.ViewCrtText
    template_name = 'core/root_certificate_managing/view.html'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View root certificate', '')
        )

    def get_initial(self):
        crt_data = self.object.crt
        key_data = self.object.key
        return {'crt': crt_data, 'key': key_data}

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)

    def get_context_data(self, **kwargs):
        cert_data = self.object.crt.encode()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
        kwargs['cert'] = cert.get_subject()
        kwargs['crt_validity_period'] = datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
        return super().get_context_data(**kwargs)


class Delete(BreadcrumbsMixin, DeleteView):
    model = models.RootCrt
    template_name = 'core/root_certificate_managing/delete.html'
    success_url = reverse_lazy('root_crt')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View certificate', reverse('root_crt_view')),
            ('Delete root certificate', '')
        )

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)


class GenerateNew(BreadcrumbsMixin, ExistsMixin, FormView):
    form_class = forms.ConfigRootCrt
    template_name = 'core/root_certificate_managing/generate_new.html'
    success_url = reverse_lazy('root_crt_view')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('root_crt')),
            ('Generate root certificate', '')
        )

    def form_valid(self, form):
        ca = Ca()
        ca.generate_root_crt(form.cleaned_data)
        return super(GenerateNew, self).form_valid(form)


class Recreate(BreadcrumbsMixin, FormView, DetailView):
    model = models.RootCrt
    form_class = forms.RecreationCrt
    template_name = 'core/certificate/recreate.html'
    success_url = reverse_lazy('root_crt_view')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View root crt', reverse('root_crt_view')),
            ('Recreation root certificate', '')
        )

    def get_object(self, queryset=None):
        return get_object_or_404(self.model)

    def form_valid(self, form):
        ca = Ca()
        ca.generate_root_crt(form.cleaned_data, recreation=True)
        messages.success(self.request, 'Recreation success')
        return super().form_valid(form)


class DownloadRootCrt(View):

    def get(self, request, *args, **kwargs):
        res = HttpResponse(models.RootCrt.objects.get().crt, content_type='text/plain')
        res['Content-Disposition'] = 'attachment; filename=rootCA.crt'
        return res
