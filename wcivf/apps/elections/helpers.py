from django.conf import settings
import requests


class EEHelper:

    ee_cache = {}

    def get_data(self, election_id):
        if election_id in self.ee_cache:
            return self.ee_cache[election_id]
        req = requests.get("{}/api/elections/{}/".format(settings.EE_BASE, election_id))
        if req.status_code == 200:
            self.ee_cache[election_id] = req.json()
            return self.ee_cache[election_id]
        else:
            self.ee_cache[election_id] = None
        return None


class JsonPaginator:
    def __init__(self, page1, stdout):
        self.next_page = page1
        self.stdout = stdout

    def __iter__(self):
        while self.next_page:
            self.stdout.write(self.next_page)

            r = requests.get(self.next_page)
            if r.status_code != 200:
                self.stdout.write("crashing with response:")
                self.stdout.write(r.content)
            r.raise_for_status()
            data = r.json()

            try:
                self.next_page = data["next"]
            except KeyError:
                self.next_page = None

            yield data

        return
