from django.conf import settings

from .forms import PostcodeLookupForm

def canonical_url(request):
    return {'CANONICAL_URL': settings.CANONICAL_URL}

def use_compress_css(request):
    return {
        'USE_COMPRESSED_CSS': getattr(settings, 'USE_COMPRESSED_CSS', False)
    }

def postcode_form(request):
    return {
        'postcode_form': PostcodeLookupForm()
    }


def referer_postcode(request):
    referer_parts = request.META.get('HTTP_REFERER', '')
    referer_parts = referer_parts.strip('/').split('/')
    if len(referer_parts) >= 2 and referer_parts[-2] == 'elections':
        return {
            'referer_postcode':
                referer_parts[-1].upper().replace('%20', ' '),
        }
    return {}
