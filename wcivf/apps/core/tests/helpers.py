import shutil
from tempfile import mkdtemp

from django.test import TestCase, override_settings
from django.conf import settings


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=mkdtemp(),
)
class TmpMediaRootMixin(TestCase):
    """
    Makes a new MEDIA_ROOT at a temporary location and cleans it up after.

    This mixin also ensures that reasonable storage backends are used for
    testing, ensuring that any local settings aren't used. This is important
    because we don't want to test deleting remote production files just
    because that's what's in the user's settings.

    """

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
