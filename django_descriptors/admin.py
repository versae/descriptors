# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.forms import BaseModelForm

from django_descriptors.models import DescribedItem


class DescriptorAdmin(admin.ModelAdmin):

    list_display = ('name', 'path')
    search_fields = ('name', )


class DescribedItemAdmin(admin.ModelAdmin):

    list_display = ('parent', 'descriptor', 'described_object', 'value')
    list_display_links = ('descriptor', )
    search_fields = ('descriptor__name', 'content_type', 'object_id',
                    'content_object', 'value')

    def parent(self, obj):
        if obj.descriptor.parent:
            return obj.descriptor.parent.name
        return u""

    def described_object(self, obj):
        return obj


class DescribedItemModelForm(forms.ModelForm):

    class Meta:
        model = DescribedItem


class DescribedItemInline(generic.GenericTabularInline):

    model = DescribedItem
    form = DescribedItemModelForm
    extra = 1
    template = 'admin/edit_inline/tabular.html'

