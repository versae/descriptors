# -*- coding: utf-8 -*-
from django.contrib import admin


class DescriptorAdmin(admin.ModelAdmin):

    list_display = ('name', )
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
