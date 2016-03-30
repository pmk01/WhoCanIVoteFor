from django.conf.urls import url

from .views import PostcodeView

urlpatterns = [
    url(
        r'^(?P<postcode>[^/]+)/$',
        PostcodeView.as_view(),
        name='postcode_view'),
]
