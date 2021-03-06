from OpenSSL import crypto

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError

from core import models
from core.utils import Ca


class RootCrt(forms.Form):
    crt = forms.FileField(label='root .crt file')
    key = forms.FileField(label='root .key file')

    def clean(self):
        cleaned_data = super().clean()
        cert_data = cleaned_data.get('crt').read()
        key_data = cleaned_data.get('key').read()
        cleaned_data.get('crt').seek(0)
        cleaned_data.get('key').seek(0)
        try:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data).get_subject()
            ca = Ca()
            if not ca.check_crt_and_key(cert_data.decode(), key_data.decode()):
                raise ValidationError('You upload a different key and certificate')
            if not cert.C or not cert.ST or not cert.L or not cert.O:
                msg = 'Please enter required field in certificate: Country, State, Location, Organization'
                self.add_error('crt', msg)
        except crypto.Error:
            raise ValidationError('Please load valid certificate and key')

        return cleaned_data


class ConfigRootCrt(forms.Form):
    country = forms.CharField(max_length=2, label='Country')
    state = forms.CharField(label='State')
    location = forms.CharField(label='Location')
    organization = forms.CharField(label='Organization')
    organizational_unit_name = forms.CharField(required=False, label='Organizational_unit_name')
    common_name = forms.CharField(required=False, label='Common name')
    email = forms.EmailField(required=False, label='Email')
    validity_period = forms.DateField(label='Certificate expiration date')

    def clean_common_name(self):
        common_name = self.cleaned_data.get('common_name')

        if '_' in common_name:
            raise forms.ValidationError('Illegal character "_"')

        return common_name


class ViewCrtText(forms.Form):
    crt = forms.CharField(widget=forms.Textarea(attrs={'rows': '8'}))
    key = forms.CharField(widget=forms.Textarea(attrs={'rows': '8'}))


class CertificatesCreate(forms.Form):
    cn = forms.CharField(required=False, label='Common name')
    validity_period = forms.DateField(label='Certificate expiration date')

    def clean_cn(self):
        cn = self.cleaned_data.get('cn')

        if '_' in cn:
            raise forms.ValidationError('Illegal character "_"')

        return cn

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('cn')
        try:
            models.SiteCrt.objects.get(cn=data)
            msg = "Common name {} not unique".format(data)
            self.add_error('cn', msg)
        except ObjectDoesNotExist:
            pass
        return cleaned_data


class CertificatesSearch(forms.Form):
    cn = forms.CharField(required=False, label='Common name')


class CertificatesUploadExisting(forms.Form):
    crt_file = forms.FileField(required=False, label='certificate .crt file')
    key_file = forms.FileField(required=False, label='certificate .key file')
    crt_text = forms.CharField(widget=forms.Textarea(attrs={'rows': '6'}), required=False, label='Certificate')
    key_text = forms.CharField(widget=forms.Textarea(attrs={'rows': '6'}), required=False, label='Key')

    def clean(self):
        cleaned_data = super().clean()
        crt_file = self.cleaned_data.get('crt_file')
        key_file = self.cleaned_data.get('key_file')
        crt_text = self.cleaned_data.get('crt_text')
        key_text = self.cleaned_data.get('key_text')
        if ((crt_file or key_file) and (crt_text or key_text)) or (not (crt_file or key_file or crt_text or key_text)):
            raise ValidationError('Please fill 2 field to choose from(File or Text)')

        if self.errors:
            return

        if crt_file:
            crt = crt_file.read()
            key = key_file.read()
            crt_file.seek(0)
            key_file.seek(0)
        else:
            crt = crt_text
            key = key_text
        crypto.load_certificate(crypto.FILETYPE_PEM, crt)
        ca = Ca()
        if not ca.check_crt_and_key(crt, key):
            raise ValidationError('You upload a different key and certificate')

        return cleaned_data

    def clean_crt_file(self):
        crt_file = self.cleaned_data.get('crt_file')
        if crt_file:
            crt_file_data = crt_file.read()
            crt_file.seek(0)
            try:
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, crt_file_data)
                try:
                    obj_crt_in_db = models.SiteCrt.objects.get(cn=cert.get_subject().CN)
                    if obj_crt_in_db:
                        msg = 'Certificate with Common name {} already exists in db'.format(cert.get_subject().CN)
                        self.add_error('crt_file', msg)
                except ObjectDoesNotExist:
                    pass
            except crypto.Error:
                raise ValidationError('Please load valid certificate and key')
        return crt_file

    def clean_crt_text(self):
        crt_text = self.cleaned_data.get('crt_text')
        if crt_text:
            try:
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, crt_text)
                try:
                    obj_crt_in_db = models.SiteCrt.objects.get(cn=cert.get_subject().CN)
                    if obj_crt_in_db:
                        msg = 'Certificate with Common name {} already exists in db'.format(cert.get_subject().CN)
                        self.add_error('crt_text', msg)
                except ObjectDoesNotExist:
                    pass
            except crypto.Error:
                raise ValidationError('Please load valid certificate and key')
        return crt_text


class RecreationCrt(forms.Form):
    validity_period = forms.DateField(label='Certificate expiration date')
