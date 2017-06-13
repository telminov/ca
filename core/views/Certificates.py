from .Base import *


class Index(RedirectView):
    url = reverse_lazy('certificates_search')


class CertificatesSearch(BreadcrumbsMixin, SortMixin, FormMixin, ListView):
    form_class = forms.CertificatesSearch
    model = models.SiteCrt
    template_name = 'core/certificates.html'
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


class CertificatesCreate(BreadcrumbsMixin, FormView):
    form_class = forms.CertificatesCreate
    success_url = reverse_lazy('certificates_search')
    template_name = 'core/certificate/create.html'

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
            ca.generate_site_crt(form.cleaned_data['cn'], form.cleaned_data['validity_period'], alt_name='IP')
        else:
            ca.generate_site_crt(form.cleaned_data['cn'], form.cleaned_data['validity_period'])
        return super().form_valid(form)


class CertificatesUploadExisting(BreadcrumbsMixin, FormView):
    template_name = 'core/certificate/upload_existing.html'
    form_class = forms.CertificatesUploadExisting
    success_url = reverse_lazy('certificates_search')

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
            Ca.write_cert_site(cert, pkey, cn)
            models.SiteCrt.objects.create(
                key=os.path.join(cn, cn + '.key'),
                crt=os.path.join(cn, cn + '.crt'),
                cn=cn,
                date_end=current_tz.localize(datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ'))
            )
        return super().form_valid(form)


class CertificatesView(BreadcrumbsMixin, FormMixin, DetailView):
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


class CertificatesDelete(BreadcrumbsMixin, DeleteView):
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

    def delete(self, request, *args, **kwargs):
        path_dir = os.path.join(settings.MEDIA_ROOT, os.path.dirname(self.get_object().crt.name))
        shutil.rmtree(path_dir)
        return super().delete(request, *args, **kwargs)


class CertificatesRecreate(BreadcrumbsMixin, FormView, DetailView):
    model = models.SiteCrt
    form_class = forms.RecreationCrt
    template_name = 'core/certificate/recreate.html'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('View %s' % models.SiteCrt.objects.get(pk=self.kwargs['pk']).cn,
             reverse('certificates_view', kwargs={'pk': self.kwargs['pk']})),
            ('Recreation certificate', '')
        )

    def get_success_url(self):
        return reverse_lazy('certificates_view', kwargs={'pk': self.kwargs['pk']})

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
        ca = Ca()
        ca.generate_site_crt(self.object.cn, form.cleaned_data['validity_period'], self.kwargs['pk'])
        messages.success(self.request, 'Recreation success')
        return super().form_valid(form)

