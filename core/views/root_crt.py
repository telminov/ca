import os
from datetime import datetime
from OpenSSL import crypto

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, FormView, DetailView, DeleteView
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


class UploadExisting(BreadcrumbsMixin, ExistsMixin, CreateView):
    form_class = forms.RootCrt
    template_name = 'core/root_certificate_managing/upload_existing.html'
    success_url = reverse_lazy('root_crt_view')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('root_crt')),
            ('Load root certificate', '')
        )


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

    def delete(self, request, *args, **kwargs):
        path_root_dir = os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH)
        directory = os.listdir(path_root_dir)
        for file in directory:
            os.remove(os.path.join(path_root_dir, file))
        return super().delete(request, *args, **kwargs)


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
        self.object = models.RootCrt.objects.get()
        path_root_dir = os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH)
        directory = os.listdir(path_root_dir)
        for file in directory:
            os.remove(os.path.join(path_root_dir, file))
        ca = Ca()
        ca.generate_root_crt(form.cleaned_data, recreation=True)
        messages.success(self.request, 'Recreation success')
        return super().form_valid(form)

