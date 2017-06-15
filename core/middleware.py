import re

from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings

from core import models

EXEMPT_URLS = [re.compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]
EXEMPT_URLS += [re.compile(expr) for expr in settings.ROOT_CRT_INTERFACE]


class RootCrtMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if any(m.match(request.path_info) for m in EXEMPT_URLS):
            return response
        if models.RootCrt.objects.exists():
            return response
        messages.info(request, 'Please create crt root')
        return HttpResponseRedirect(reverse_lazy('root_crt'))
