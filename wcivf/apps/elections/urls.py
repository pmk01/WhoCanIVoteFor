from django.conf.urls import url

from .views import (
    PostcodeView,
    ElectionsView,
    ElectionView,
    PostView,
    PostcodeiCalView,
)
from .helpers import ElectionIDSwitcher

urlpatterns = [
    url(r"^$", ElectionsView.as_view(), name="elections_view"),
    url(
        "^(?P<election>[a-z\-]+\.[^/]+)(?:/(?P<ignored_slug>[^/]+))?/$",
        ElectionIDSwitcher(election_view=ElectionView, ballot_view=PostView),
        name="election_view",
    ),
    url(
        r"^(?P<postcode>[^/]+)/$", PostcodeView.as_view(), name="postcode_view"
    ),
    url(
        r"^(?P<postcode>[^/]+).ics$",
        PostcodeiCalView.as_view(),
        name="postcode_ical_view",
    ),
]
