from django.conf import settings
import requests


class EEHelper:

    ee_cache = {}

    def get_data(self, election_id):
        if election_id in self.ee_cache:
            return self.ee_cache[election_id]
        req = requests.get(
            '{}/api/elections/{}/'.format(
                settings.EE_BASE,
                election_id)
            )
        if req.status_code == 200:
            self.ee_cache[election_id] = req.json()
            return self.ee_cache[election_id]
        else:
            self.ee_cache[election_id] = None
        return None
