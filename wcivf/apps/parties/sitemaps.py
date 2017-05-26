from django.contrib.sitemaps import Sitemap
from .models import Party


class PartySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Party.objects.all()
