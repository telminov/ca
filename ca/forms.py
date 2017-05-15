from django import forms

from ca import models


class RootCrt(forms.ModelForm):
    class Meta:
        model = models.RootCrt
        fields = ('key', 'crt')
