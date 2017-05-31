import os
import shutil

from django.test.runner import DiscoverRunner
from django.conf import settings


class TempMediaMixin(DiscoverRunner):

    def setup_test_environment(self, **kwargs):
        super(TempMediaMixin, self).setup_test_environment()
        settings._original_media_root = settings.MEDIA_ROOT
        self._temp_media = '/tmp/test/'
        settings.MEDIA_ROOT = self._temp_media

    def teardown_test_environment(self, **kwargs):
        if os.path.exists('/tmp/test/'):
            shutil.rmtree('/tmp/test/')
