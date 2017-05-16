from OpenSSL import crypto

from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.views.generic import TemplateView, CreateView, DeleteView, FormView

from ca.utils import create_self_signed_cert_root
from ca import forms
from ca import models


class RootAlreadyExist(object):
    def render_to_response(self, context, **response_kwargs):
        if models.RootCrt.objects.first():
            return TemplateResponse(request=self.request, template='ca/root_already_exists.html')
        else:
            return super().render_to_response(context, **response_kwargs)


class IndexRootCrt(RootAlreadyExist, TemplateView):
    template_name = 'ca/index.html'


class LoadRootCrt(RootAlreadyExist, CreateView):
    form_class = forms.RootCrt
    template_name = 'ca/has_root_key.html'
    success_url = reverse_lazy('view_root_crt')


class ViewRootCrt(TemplateView):
    template_name = 'ca/view_root_crt.html'
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        # предполагается, что такой объект только один
        models.RootCrt.objects.first().delete()
        return HttpResponseRedirect(force_text(self.success_url))

    def get_context_data(self, **kwargs):
        context = super(ViewRootCrt, self).get_context_data(**kwargs)

        st_cert = open('media/' + str(models.RootCrt.objects.first().crt), 'rt').read()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, st_cert)

        context['C'] = cert.get_subject()
        return context


class GenerateRootCrt(RootAlreadyExist, FormView):
    form_class = forms.ConfigRootCrt
    template_name = 'ca/no_root_key.html'
    success_url = reverse_lazy('view_root_crt')

    def form_valid(self, form):
        create_self_signed_cert_root(form.cleaned_data)
        return super(GenerateRootCrt, self).form_valid(form)
