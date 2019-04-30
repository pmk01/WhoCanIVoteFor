from django.db import models
from django.db.models import Count
from django.core.cache import cache
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

from elections.constants import PEOPLE_FOR_BALLOT_KEY_FMT


class PersonPostQuerySet(models.QuerySet):
    def by_party(self):
        return self.order_by("party__party_name", "list_position")

    def elected(self):
        return self.filter(elected=True)

    def counts_by_post(self):
        return (
            self.values(
                "post__label",
                "post_id",
                "election__slug",
                "election__name",
                "post_election__cancelled",
            )
            .annotate(num_candidates=Count("person"))
            .order_by("-election__election_date", "post__label")
        )


class PersonPostManager(models.Manager):
    def get_queryset(self):
        return PersonPostQuerySet(self.model, using=self._db)

    def by_party(self):
        return self.get_queryset().by_party()

    def elected(self):
        return self.get_queryset().elected()

    def counts_by_post(self):
        return self.get_queryset().counts_by_post()


class PersonManager(models.Manager):
    def update_or_create_from_ynr(
        self, person, all_ballots, all_parties, update_info_only=False
    ):

        last_updated = make_aware(
            parse_datetime(person["versions"][0]["timestamp"])
        )

        defaults = {
            "name": person["name"],
            "email": person["email"] or None,
            "gender": person["gender"] or None,
            "birth_date": person["birth_date"] or None,
            "last_updated": last_updated,
        }

        version_data = person["versions"][0]["data"]
        if "twitter_username" in version_data:
            defaults["twitter_username"] = version_data["twitter_username"]
        if "facebook_page_url" in version_data:
            defaults["facebook_page_url"] = version_data["facebook_page_url"]
        if "facebook_personal_url" in version_data:
            defaults["facebook_personal_url"] = version_data[
                "facebook_personal_url"
            ]
        if "linkedin_url" in version_data:
            defaults["linkedin_url"] = version_data["linkedin_url"]
        if "homepage_url" in version_data:
            defaults["homepage_url"] = version_data["homepage_url"]
        if "party_ppc_page_url" in version_data:
            defaults["party_ppc_page_url"] = version_data["party_ppc_page_url"]
        if "wikipedia_url" in version_data:
            defaults["wikipedia_url"] = version_data["wikipedia_url"]
        if "biography" in version_data:
            defaults["statement_to_voters"] = version_data["biography"]
        if "thumbnail" in person:
            defaults["photo_url"] = person["thumbnail"]
        if (
            "extra_fields" in version_data
            and "favourite_biscuits" in version_data["extra_fields"]
        ):
            defaults["favourite_biscuit"] = version_data["extra_fields"][
                "favourite_biscuits"
            ]
        if "identifiers" in version_data:
            for i in version_data["identifiers"]:
                if i["scheme"] == "uk.org.publicwhip":
                    defaults["twfy_id"] = i["identifier"].replace(
                        "uk.org.publicwhip/person/", ""
                    )

        person_id = person["id"]
        person_obj, _ = self.update_or_create(
            ynr_id=person["id"], defaults=defaults
        )

        if not update_info_only:
            from .models import PersonPost

            person_posts = PersonPost.objects.filter(person_id=person_id)
            ballots_ids_to_invalidate = [
                pp.post_election.ballot_paper_id for pp in person_posts
            ]

            # Delete old posts for this person
            person_posts.delete()

            if person["memberships"]:
                for membership in person["memberships"]:

                    if membership.get("ballot_paper_id"):
                        ballot = all_ballots[membership["ballot_paper_id"]]
                        defaults = {
                            "list_position": membership["party_list_position"],
                            "party": all_parties[
                                membership["party"]["legacy_slug"]
                            ],
                            "post": ballot.post,
                            "election": ballot.election,
                        }

                        PersonPost.objects.update_or_create(
                            person_id=person_id,
                            post_election=ballot,
                            defaults=defaults,
                        )

            # Delete the cache for this person's ballots as the membership might
            # have changed
            for ballot_paper_id in ballots_ids_to_invalidate:
                cache.delete(PEOPLE_FOR_BALLOT_KEY_FMT.format(ballot_paper_id))

        return person_obj
