from django.conf.urls import url, include

from rest_framework import routers

from api import views

router = routers.DefaultRouter()

router.register(r"people", views.PersonViewSet)

router.register(
    r"candidates_for_postcode",
    views.CandidatesAndElectionsForPostcodeViewSet,
    base_name="candidates-for-postcode",
)
router.register(
    r"candidates_for_ballots",
    views.CandidatesAndElectionsForBallots,
    base_name="candidates-for-ballots",
)


urlpatterns = [url(r"^", include(router.urls))]
