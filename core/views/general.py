from django.urls import reverse_lazy
from django.views.generic import RedirectView


class Index(RedirectView):
    url = reverse_lazy('certificates_search')
