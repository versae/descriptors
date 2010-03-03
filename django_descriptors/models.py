# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from django.utils import simplejson


class DescriptorManager(models.Manager):

    def add_descriptor(self, obj, descriptor_item):
        return self.add_descriptors(obj, [descriptors_item])

    def add_descriptors(self, obj, descriptors_list, json=False):
        if json:
            descriptors_list = simplejson.loads(descriptors_list)
        for descriptor_tuple in descriptors_list:
            object_id = descriptor_tuple[0]
            descriptor = Descriptor.objects.in_bulk([object_id]).get(object_id,
                                                                     None)
            value = descriptor_tuple[1]
            if object_id and descriptor and value:
                content_type = ContentType.objects.get_for_model(obj)
                item_args = {
                    "descriptor": descriptor,
                    "value": value,
                    "content_type": content_type,
                    "content_object": obj,
                    "object_id": object_id,
                }
                described_item = DescribedItem.objects.create(**item_args)
                described_item.save()

    def get_for_object(self, obj):
        """
        Create a queryset matching all descriptors associated with the given
        object.
        """
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(items__content_type__pk=ctype.pk,
                           items__object_id=obj.pk)


class Descriptor(models.Model):
    """
    A descriptor.
    """
    name = models.CharField(_('name'), max_length=100, unique=True,
                            db_index=True)
    parent = models.ForeignKey('self', verbose_name=_(u'parent'), blank=True,
                               null=True)
    description = models.TextField(_('description'), blank=True)

    objects = DescriptorManager()

    class Meta:
        ordering = ('name', )
        verbose_name = _('descriptor')
        verbose_name_plural = _('descriptors')

    def __unicode__(self):
        return self.name


class DescribedItem(models.Model):
    """
    Holds the relationship between a descriptor and the item being described.
    """
    descriptor = models.ForeignKey(Descriptor, verbose_name=_('descriptor'),
                                   related_name='items')
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    value = models.CharField(_('value'), max_length=250)

    class Meta:
        # Enforce unique description association per object
        unique_together = (('descriptor', 'content_type', 'object_id'), )
        verbose_name = _('described item')
        verbose_name_plural = _('described items')

    def __unicode__(self):
        return u'%s [%s]' % (self.content_object, self.descriptor)
