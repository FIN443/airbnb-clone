from django import forms
from django.utils.translation import gettext_lazy as _


class AddCommentForm(forms.Form):

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={"placeholder": _("Write a Message"), "style": "height: 150px;"}
        ),
    )
