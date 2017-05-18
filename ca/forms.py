from django import forms

from ca import models


class RootCrt(forms.ModelForm):
    class Meta:
        model = models.RootCrt
        fields = ('key', 'crt')
        labels = {
            'key' : 'root .key file',
            'crt' : 'root .crt file'
        }

class ConfigRootCrt(forms.Form):
    country = forms.CharField(max_length=2)
    state = forms.CharField()
    location = forms.CharField()
    organization = forms.CharField()
    organizational_unit_name = forms.CharField(required=False)
    cn = forms.CharField()
    email = forms.EmailField(required=False)
