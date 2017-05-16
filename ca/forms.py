from django import forms

from ca import models


class RootCrt(forms.ModelForm):
    class Meta:
        model = models.RootCrt
        fields = ('key', 'crt')


class ConfigRootCrt(forms.Form):
    Country = forms.CharField()
    State = forms.CharField()
    Location = forms.CharField()
    Organization = forms.CharField()
    Organizational_Unit_Name = forms.CharField(required=False)
    CN = forms.CharField()
    email = forms.EmailField(required=False)
