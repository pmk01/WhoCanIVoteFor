from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from .views import HomePageView, StatusCheckView, OpenSearchView

urlpatterns = [
    url(r"^$", HomePageView.as_view(), name="home_view"),
    url(
        r"^privacy/$",
        RedirectView.as_view(
            url="https://democracyclub.org.uk/privacy/", permanent=True
        ),
        name="privacy_view",
    ),
    url(
        r"^about/$",
        TemplateView.as_view(template_name="about.html"),
        name="about_view",
    ),
    url(
        r"^standing/$",
        TemplateView.as_view(template_name="standing.html"),
        name="standing_as_a_candidate",
    ),
    url(
        r"^_status_check/$", StatusCheckView.as_view(), name="status_check_view"
    ),
    url(r"^opensearch\.xml", OpenSearchView.as_view(), name="opensearch"),
]
