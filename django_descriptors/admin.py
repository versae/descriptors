# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.contenttypes import generic

from django_descriptors.models import Descriptor, DescribedItem
from django_descriptors.widgets import Combobox


class DescriptorAdminModelForm(forms.ModelForm):

    class Meta:
        model = Descriptor
        widgets = {
            'parent': Combobox(),
        }


class DescriptorAdmin(admin.ModelAdmin):

    form = DescriptorAdminModelForm
    list_display = ('name', 'path')
    search_fields = ('name', )
    related_search_fields = {
        'parent': ('name', 'path'),
    }


class DescribedItemModelForm(forms.ModelForm):

    class Meta:
        model = DescribedItem
        widgets = {
            'descriptor': Combobox(),
        }


class DescribedItemInline(generic.GenericTabularInline):

    model = DescribedItem
    form = DescribedItemModelForm
    extra = 0
    # Add combobox in selects from inlines
    template = "admin/tabular.html"
