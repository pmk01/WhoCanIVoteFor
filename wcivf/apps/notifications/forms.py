from django import forms

from localflavor.gb.forms import GBPostcodeField

from .models import ElectionNotification

class PostcodeNotificationForm(forms.ModelForm):
    class Meta:
        model = ElectionNotification
        fields = ['postcode', 'email']

    postcode = GBPostcodeField(label="Enter your postcode")
    form_name = forms.CharField(initial="postcode_notification", widget=forms.HiddenInput)
