from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, UpdateView
from django.utils.http import is_safe_url
from django.contrib import messages
from django.template.loader import render_to_string

from .forms import FeedbackForm
from .models import Feedback
from donations.forms import DonationForm
from donations.helpers import GoCardlessHelper


class FeedbackFormView(UpdateView):
    form_class = FeedbackForm
    template_name = "feedback/feedback_form_view.html"
    donate_form_prefix = "donation_form"

    def post(self, request, *args, **kwargs):

        key_to_check = "{}-amount".format(self.donate_form_prefix)
        if key_to_check in request.POST:
            form = DonationForm(
                data=request.POST, prefix=self.donate_form_prefix)
            if form.is_valid():
                gc = GoCardlessHelper()
                url = gc.get_payment_url(**form.cleaned_data)
                return HttpResponseRedirect(url)
        return super(FeedbackFormView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        token = self.request.POST.get('token')
        try:
            return Feedback.objects.get(token=token)
        except Feedback.DoesNotExist:
            return Feedback()

    def get_success_url(self):

        feedback_object = self.object
        context = {
            'object': feedback_object,
            'donate_form': DonationForm(
                initial={
                    'payment_type': 'subscription',
                    'amount': 3,
                },
                prefix="donation_form"
            )
        }

        messages.success(
            self.request,
            render_to_string(
                'feedback/feedback_thanks.html',
                context,
                request=self.request
            ),
            extra_tags='template',
        )

        if is_safe_url(self.object.source_url):
            return self.object.source_url
        else:
            return "/"


class RecordJsonFeedback(View):
    def post(self, request):
        found_useful = request.POST.get('found_useful')
        source_url = request.POST.get('source_url')
        token = request.POST.get('token')
        Feedback.objects.update_or_create(
            token=token,
            defaults={
                'found_useful': found_useful,
                'source_url': source_url,
            }
        )
        return HttpResponse()

