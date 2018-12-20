from django.conf.urls import url

from .views import PersonView, EmailPersonView

urlpatterns = [
    url(
        r"^(?P<pk>[^/]+)/email/(?P<ignored_slug>.*)$",
        EmailPersonView.as_view(),
        name="email_person_view",
    ),
    url(
        r"^(?P<pk>[^/]+)/(?P<ignored_slug>.*)$",
        PersonView.as_view(),
        name="person_view",
    ),
]
