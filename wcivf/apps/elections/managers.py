from django.db import models
from django.conf import settings

import requests


class ElectionManager(models.Manager):

    def get_explainer_from_ee(self, election):
        req = requests.get(
            '{}/api/elections/{}/'.format(
                settings.EE_BASE,
                election['id'])
            )
        if req.status_code == 200:
            description = req.json()['explanation']
            if description:
                return description
        return election['description']


    def update_or_create_from_ynr(self, election):
        election_type = self.election_id_to_type(election['id'])

        election_weight = 10
        if election['party_lists_in_use']:
            election_weight = 20
        if election_type == 'mayor':
            election_weight = 5

        description = self.get_explainer_from_ee(election)

        return self.update_or_create(
            slug=election['id'],
            defaults={
                'election_date': election['election_date'],
                'name': election['name'].replace('2016', '').strip(),
                'current': election['current'],
                'description': description,
                'election_type': election_type,
                'uses_lists': election['party_lists_in_use'],
                'for_post_role': election['for_post_role'],
                'election_weight': election_weight,
            }
        )

    def election_id_to_type(self, election_id):
        parts = election_id.split('.')
        return parts[0]


class PostManager(models.Manager):
    def update_or_create_from_ynr(self, post_dict):
        from .models import Election, PostElection
        post, created = self.update_or_create(
            ynr_id=post_dict['id'],
            defaults={
                'label': post_dict['label'],
                'role': post_dict['role'],
                'group': post_dict['group'],
                'organization': post_dict['organization']['name'],
                'area_name': post_dict['area']['name'],
                'area_id': post_dict['area']['identifier'],
            }
        )

        for election_dict in post_dict['elections']:
            election = Election.objects.get(slug=election_dict['id'])
            kwargs = {}
            if post_dict['candidates_locked']:
                if election_dict['winner_count'] == \
                        len(post_dict['memberships']):
                    kwargs['contested'] = False

            PostElection.objects.update_or_create(
                election=election,
                post=post,
                defaults=kwargs
            )
        return (post, created)
