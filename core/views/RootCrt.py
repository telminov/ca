from .Base import *


class RootCrtExists(TemplateView):
    template_name = 'core/root_certificate_managing/already_exists.html'


class RootCrtExistsMixin:
    def get(self, request, *args, **kwargs):
        if models.RootCrt.objects.exists():
            return HttpResponseRedirect(reverse_lazy('root_crt_exists'))
        return super().get(request, *args, **kwargs)


class RootCrt(RootCrtExistsMixin, TemplateView):
    template_name = 'core/root_certificate_managing/crt_choice.html'


class RootCrtUploadExisting(BreadcrumbsMixin, RootCrtExistsMixin, CreateView):
    form_class = forms.RootCrt
    template_name = 'core/root_certificate_managing/upload_existing.html'
    success_url = reverse_lazy('root_crt_view')

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('root_crt')),
            ('Load root certificate', '')
        )


class RootCrtView(BreadcrumbsMixin, FormMixin, DetailView):
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


class RootCrtDelete(BreadcrumbsMixin, DeleteView):
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


class RootCrtGenerateNew(BreadcrumbsMixin, RootCrtExistsMixin, FormView):
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
        return super(RootCrtGenerateNew, self).form_valid(form)


class RootCrtRecreate(BreadcrumbsMixin, FormView, DetailView):
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

