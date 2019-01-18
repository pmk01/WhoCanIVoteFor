import re

import requests

from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.core.cache import cache

from core.models import log_postcode
from people.models import PersonPost
from elections.constants import UPDATED_SLUGS


class PostcodeToPostsMixin(object):
    def get(self, request, *args, **kwargs):
        from ..models import InvalidPostcodeError

        try:
            context = self.get_context_data(**kwargs)
        except InvalidPostcodeError:
            return HttpResponseRedirect(
                "/?invalid_postcode=1&postcode={}".format(self.postcode)
            )
        return self.render_to_response(context)

    def clean_postcode(self, postcode):
        postcode = postcode.replace("+", "")
        incode_pattern = "[0-9][ABD-HJLNP-UW-Z]{2}"
        space_regex = re.compile(r" *(%s)$" % incode_pattern)
        postcode = space_regex.sub(r" \1", postcode.upper())
        return postcode

    def postcode_to_posts(self, postcode, compact=False):
        key = "upcoming_elections_{}".format(postcode.replace(" ", ""))
        results_json = cache.get(key)
        if not results_json:
            url = "{0}/api/elections?postcode={1}&current=1".format(
                settings.EE_BASE, postcode
            )
            req = requests.get(url)

            # Don't cache bad postcodes
            from ..models import InvalidPostcodeError

            if req.status_code != 200:
                raise InvalidPostcodeError(postcode)

            results_json = req.json()["results"]
            cache.set(key, results_json)

        all_posts = []
        all_elections = []
        for election in results_json:

            # Convert an EE election dict in to a YNR ID
            if election["division"]:
                post_id = ":".join(
                    [
                        election["division"]["division_type"],
                        election["division"]["official_identifier"].split(":")[-1],
                    ]
                )
                all_elections.append(election["group"])
            else:
                post_id = election["organisation"]["slug"]
                all_elections.append(election["election_id"])

            all_posts.append(post_id)

        from ..models import PostElection

        pes = PostElection.objects.filter(
            post__ynr_id__in=all_posts, election__slug__in=all_elections
        )
        pes = pes.select_related("post")
        pes = pes.select_related("election")
        pes = pes.select_related("election__voting_system")
        if not compact:
            pes = pes.prefetch_related("husting_set")
        pes = pes.order_by("election__election_date", "election__election_weight")

        return pes


class PostelectionsToPeopleMixin(object):
    def postelections_to_people(self, postelection):
        key = "person_posts_{}".format(postelection.post.ynr_id)
        people_for_post = cache.get(key)
        if people_for_post:
            return people_for_post

        people_for_post = PersonPost.objects.filter(
            post=postelection.post, election=postelection.election
        )

        if postelection.election.uses_lists:
            order_by = ["party__party_name", "list_position"]
        else:
            order_by = ["person__name"]
        people_for_post = people_for_post.order_by("-elected", *order_by)
        people_for_post = people_for_post.select_related(
            "post", "election", "person", "party", "person__cv", "results"
        ).prefetch_related("person__leaflet_set", "person__pledges")
        cache.set(key, people_for_post)
        return people_for_post


class PollingStationInfoMixin(object):
    def get_polling_station_info(self, postcode):
        key = "pollingstations_{}".format(postcode.replace(" ", ""))
        info = cache.get(key)
        if info:
            return info

        info = {}
        base_url = settings.WDIV_BASE + settings.WDIV_API
        url = "{}/postcode/{}.json?auth_token={}".format(
            base_url, postcode, getattr(settings, "WDIV_API_KEY", "DCINTERNAL-WHO")
        )
        try:
            req = requests.get(url)
        except:
            return info
        if req.status_code != 200:
            return info
        info.update(req.json())
        cache.set(key, info)
        return info


class LogLookUpMixin(object):
    def log_postcode(self, postcode):
        kwargs = {"postcode": postcode}
        kwargs.update(self.request.session["utm_data"])
        log_postcode(kwargs)

class NewSlugsRedirectMixin(object):
    def get_changed_election_slug(self, slug):
        return UPDATED_SLUGS.get(slug, slug)

    def get(self, request, *args, **kwargs):
        given_slug = self.kwargs.get(self.pk_url_kwarg)
        updated_slug = self.get_changed_election_slug(given_slug)
        if updated_slug != given_slug:
            return HttpResponsePermanentRedirect(
                reverse("election_view", kwargs={"election": updated_slug})
            )

        return super().get(request, *args, **kwargs)
