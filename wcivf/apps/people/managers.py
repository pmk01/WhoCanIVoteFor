from django.db import models
from django.db.models import Count
from django.utils.dateparse import parse_datetime


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
    def update_or_create_from_ynr(self, person, update_info_only=False):

        last_updated = parse_datetime(person["last_updated"])

        defaults = {
            "name": person["name"],
            "email": person["email"] or None,
            "gender": person["gender"] or None,
            "birth_date": person["birth_date"] or None,
            "last_updated": last_updated,
        }

        value_types_to_import = [
            "twitter_username",
            "facebook_page_url",
            "facebook_personal_url",
            "linkedin_url",
            "homepage_url",
            "party_ppc_page_url",
            "wikipedia_url",
            "theyworkforyou",
            "youtube_profile",
            "instagram_url",
        ]

        for value_type in value_types_to_import:
            defaults[value_type] = None
        del defaults["theyworkforyou"]

        for identifier in person["identifiers"]:
            value_type = identifier["value_type"]

            if value_type in value_types_to_import:
                if value_type == "theyworkforyou":
                    defaults["twfy_id"] = identifier[
                        "internal_identifier"
                    ].replace("uk.org.publicwhip/person/", "")
                else:
                    defaults[value_type] = identifier["value"]

        defaults["statement_to_voters"] = person["statement_to_voters"]
        defaults["favourite_biscuit"] = person["favourite_biscuit"]

        if "thumbnail" in person:
            defaults["photo_url"] = person["thumbnail"]

        person_id = person["id"]
        person_obj, _ = self.update_or_create(
            ynr_id=person_id, defaults=defaults
        )
        return person_obj
