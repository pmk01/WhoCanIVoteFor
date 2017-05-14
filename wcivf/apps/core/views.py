import json
import os

from django import http
from django.conf import settings
from django.views.generic import View, FormView
from django.core.urlresolvers import reverse

from .forms import PostcodeLookupForm


class PostcodeFormView(FormView):
    form_class = PostcodeLookupForm

    def get(self, request, *args, **kwargs):
        if 'postcode' in request.GET \
                and 'invalid_postcode' not in self.request.GET:
            redirect_url = reverse(
                'postcode_view',
                kwargs={'postcode': request.GET['postcode']}
            )
            return http.HttpResponseRedirect(redirect_url)
        return super(PostcodeFormView, self).get(request, *args, **kwargs)

    def get_initial(self):
        initial = self.initial.copy()
        if 'invalid_postcode' in self.request.GET:
            initial['postcode'] = self.request.GET.get('postcode')
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'autofocus': True})
        return kwargs

    def form_valid(self, form):
        postcode = form.cleaned_data['postcode']
        self.success_url = reverse(
            'postcode_view',
            kwargs={'postcode': postcode}
        )
        return super().form_valid(form)


class HomePageView(PostcodeFormView):
    template_name = "home.html"


class StatusCheckView(View):

    @property
    def server_is_dirty(self):
        if getattr(settings, 'CHECK_HOST_DIRTY', False):
            dirty_file_path = os.path.expanduser(
                getattr(settings, 'DIRTY_FILE_PATH'))

            if os.path.exists(dirty_file_path):
                return True
        return False

    def get(self, request, *args, **kwargs):

        status = 503

        data = {
            'ready_to_serve': False,
        }

        if not self.server_is_dirty:
            status = 200
            data['ready_to_serve'] = True

        return http.JsonResponse(data, status=status)
