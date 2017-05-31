from django.core.exceptions import ObjectDoesNotExist

from core import models


def ca_context_processor(request):
    try:
        return {'root_crt': models.RootCrt.objects.get()}
    except ObjectDoesNotExist:
        return {}
