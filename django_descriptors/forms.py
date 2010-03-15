"""
Descriptors components for Django's form library.
"""
from django import forms
from django.utils.translation import ugettext as _

from django_descriptors.models import Descriptor


class DescriptorAdminForm(forms.ModelForm):
    class Meta:
        model = Descriptor


class DescriptorField(forms.CharField):
    """
    A ``CharField`` which validates that its input is a valid list of
    descriptors.
    """
    pass
