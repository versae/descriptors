# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import signals
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from django.utils import simplejson


class DescriptorManager(models.Manager):

    def add_descriptor(self, obj, descriptor_item):
        return self.add_descriptors(obj, [descriptor_item])

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

    def get_html_tree(self, obj=None):
        if not obj:
            roots = self.filter(parent__isnull=True)
            subtrees = []
            for root in roots:
                subtrees.append(self.get_html_tree(root))
            return u"".join(subtrees)
        else:
            children = self.filter(parent=obj)
            lis = []
            for child in children:
                lis.append(self.get_html_tree(child))
            ul = u"<ul><li>%s%s</li></ul>" % (obj.name, u"".join(lis))
            return ul


class Descriptor(models.Model):
    """
    A descriptor.
    """
    name = models.CharField(_('name'), max_length=100, unique=True,
                            db_index=True)
    parent = models.ForeignKey('self', verbose_name=_(u'parent'), blank=True,
                               null=True)
    # Denormalized field
    path = models.TextField(_('path'), unique=True, editable=False)
    description = models.TextField(_('description'), blank=True)

    objects = DescriptorManager()

    class Meta:
        ordering = ('path', 'name')
        verbose_name = _('descriptor')
        verbose_name_plural = _('descriptors')

    def __unicode__(self):
        return self.path


def save_descriptor_path(**kwargs):
    """
    Build the path of an element to its root.
    """
    instance = kwargs['instance']
    if instance.parent:
        instance.path = u"%s → %s" % (instance.parent.path, instance.name)
    else:
        instance.path = u"[ %s ]" % instance.name
signals.pre_save.connect(save_descriptor_path, Descriptor)


class DescribedItem(models.Model):
    """
    Hold the relationship between a descriptor and the item being described.
    """
    descriptor = models.ForeignKey(Descriptor, verbose_name=_('descriptor'),
                                   related_name='items')
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    value = models.CharField(_('value'), max_length=250, null=True, blank=True)

    class Meta:
        # Enforce unique (description, value) pair association per object
        unique_together = (('descriptor', 'content_type', 'object_id',
                            'value'), )
        verbose_name = _('described item')
        verbose_name_plural = _('described items')

    def __unicode__(self):
        if self.value:
            return u'%s # %s: %s' % (self.content_object, self.descriptor,
                                     self.value)
        else:
            return u'%s # %s' % (self.content_object, self.descriptor)
