import shutil
import os
from datetime import datetime, timedelta
from OpenSSL import crypto
from djutils.views.generic import SortMixin

from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, FormView, DetailView, DeleteView, ListView, RedirectView
from django.views.generic.edit import FormMixin, ContextMixin

from core.utils import Ca
from core import forms
from core import models


class BreadcrumbsMixin(ContextMixin):
    def get_breadcrumbs(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context

