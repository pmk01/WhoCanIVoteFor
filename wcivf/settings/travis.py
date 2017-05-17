# Use normal pipeline on travis as it doesn't work with fingerprinting
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
