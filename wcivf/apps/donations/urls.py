from django.conf.urls import url

from .views import (
    DonateFormView,
    DonateThanksView,
    ProcessDonationView,
    StripeTokenProcessView,
    StripeErrorView,
)

urlpatterns = [
    url(r"thanks", DonateThanksView.as_view(), name="donate_thanks"),
    url(r"process$", ProcessDonationView.as_view(), name="donate_process"),
    url(
        r"process_stripe",
        StripeTokenProcessView.as_view(),
        name="donate_stripe_process",
    ),
    url(r"stripe_failed", StripeErrorView.as_view(), name="stripe_failed"),
    url(r"", DonateFormView.as_view(), name="donate"),
]
