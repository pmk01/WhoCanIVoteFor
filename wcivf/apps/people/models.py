from django.db import models

from elections.models import Election, Post


class PersonManager(models.Manager):
    def get_or_create_from_ynr(self, person):
        posts = []
        elections = []

        defaults = {
            'name': person['name'],
            'email': person['email'] or None,
            'gender': person['gender'] or None,
            'birth_date': person['birth_date'] or None,
        }
        if person['memberships']:
            for membership in person['memberships']:
                if membership['election']:
                    election, _ = Election.objects.get_or_create(
                        slug=membership['election']['id'],
                        name=membership['election']['name'],
                    )
                elections.append(election)
                if membership['post']:
                    post, _ = Post.objects.get_or_create(
                        ynr_id=membership['post']['id'],
                        label=membership['post']['label'],
                    )
                posts.append(post)

            if person['memberships'][0]['on_behalf_of']:
                defaults['party_name'] = person['memberships'][0]['on_behalf_of']['name']

        person, _ = self.get_or_create(
            ynr_id=person['id'],
            defaults=defaults
        )
        if posts:
            person.posts.add(*posts)
        if elections:
            person.elections.add(*elections)
        return (person, _)


class Person(models.Model):
    ynr_id = models.CharField(max_length=255, db_index=True)
    name = models.CharField(blank=True, max_length=255)
    email = models.EmailField(null=True)
    gender = models.CharField(blank=True, max_length=255, null=True)
    birth_date = models.CharField(null=True, max_length=255)

    # TODO Turn parties in to a model/app
    party_name = models.CharField(blank=True, max_length=255)

    posts = models.ManyToManyField(Post)

    elections = models.ManyToManyField(Election)

    objects = PersonManager()

    def __str__(self):
        return self.name
