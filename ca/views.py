from OpenSSL import crypto

from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DeleteView, FormView

from ca.utils import create_self_signed_cert_root
from ca import forms
from ca import models

from django.shortcuts import render


# Запилить миксин, который проверяет существование сертификата рута, если он есть грузить заглушку
class IndexRootCrt(TemplateView):
    template_name = 'ca/index.html'


class LoadRootCrt(CreateView):
    form_class = forms.RootCrt
    template_name = 'ca/has_root_key.html'
    success_url = reverse_lazy('view_root_crt')


class ViewRootCrt(DeleteView):
    template_name = 'ca/view_root_crt.html'
    success_url = reverse_lazy('has_root_key')
    model = models.RootCrt

    def get_object(self, queryset=None):
        # предполагается, что такой объект только один
        obj = models.RootCrt.objects.first()
        return obj

    def get_context_data(self, **kwargs):
        context = super(ViewRootCrt, self).get_context_data(**kwargs)

        st_cert = open('media/' + str(models.RootCrt.objects.first().crt), 'rt').read()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, st_cert)

        context['C'] = cert.get_subject()
        return context


class GenerateRootCrt(FormView):
    form_class = forms.ConfigRootCrt
    template_name = 'ca/no_root_key.html'
    success_url = reverse_lazy('view_root_crt')

    def form_valid(self, form):
        create_self_signed_cert_root(form.cleaned_data)
        return super(GenerateRootCrt, self).form_valid(form)


def root_already_exists(request):
    return render(request, 'ca/root_already_exists.html')
