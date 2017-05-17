from django import forms

from ca import models


class RootCrt(forms.ModelForm):
    class Meta:
        model = models.RootCrt
        fields = ('key', 'crt')


class ConfigRootCrt(forms.Form):
    country = forms.CharField()
    state = forms.CharField()
    location = forms.CharField()
    organization = forms.CharField()
    organizational_unit_name = forms.CharField(required=False)
    cn = forms.CharField()
    email = forms.EmailField(required=False)
