"""
A custom Model Field for descriptors.
"""
from django.db.models import signals
from django.db.models.fields import CharField
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson

from django_descriptors.models import Descriptor, DescribedItem
from django_descriptors.utils import edit_string_for_descriptors


class DescriptorField(CharField):
    """
    A "special" character field that actually works as a relationship to
    descriptors "under the hood". This exposes a space-separated string of
    descriptors, but does the splitting/reordering/etc. under the hood.
    """
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 255)
        kwargs['blank'] = kwargs.get('blank', True)
        kwargs['default'] = kwargs.get('default', '')
        super(DescriptorField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(DescriptorField, self).contribute_to_class(cls, name)

        # Make this object the descriptor for field access.
        setattr(cls, self.name, self)

        # Save descriptors back to the database post-save
        signals.post_save.connect(self._save, cls, True)

        # Update descriptors from descriptor objects post-init
        signals.post_init.connect(self._update, cls, True)

    def __get__(self, instance, owner=None):
        """
        descriptor getter. Returns an instance's descriptors if accessed on an
        instance, and all of a model's descriptors if called on a class. That
        is, this model::

           class Link(models.Model):
               ...
               descriptors = descriptorField()

        Lets you do both of these::

           >>> l = Link.objects.get(...)
           >>> l.descriptors
           '[[1,"value1"],[2,"value2"]]'

           >>> Link.descriptors
           '[[1,"value1"],[2,"value2"]],[3,"value3"]],[4,"value4"]]'

        """
        # Handle access on the model
        if instance is None:
            return u""
        return self._get_instance_descriptors_cache(instance)

    def __set__(self, instance, value):
        """
        Set an object's descriptors.
        """
        if instance is None:
            raise AttributeError(_('%s can only be set on instances.') % self.name)
        self._set_instance_descriptors_cache(instance, value)

    def _save(self, **kwargs): # signal, sender, instance
        """
        Save descriptors back to the database
        """
        instance = kwargs['instance']
        descriptors_json = self._get_instance_descriptors_cache(instance)
        Descriptor.objects.add_descriptors(instance, descriptors_json,
                                           json=True)

    def _update(self, **kwargs): # signal, sender, instance
        """
        Update descriptor cache from descriptorgedItem objects.
        """
        instance = kwargs['instance']
        self._update_instance_descriptor_cache(instance)

    def __delete__(self, instance):
        """
        Clear all of an object's descriptors.
        """
        self._set_instance_descriptors_cache(instance, '')

    def _get_instance_descriptors_cache(self, instance):
        """
        Helper: get an instance's descriptor cache.
        """
        return getattr(instance, '_%s_cache' % self.attname, None)

    def _set_instance_descriptors_cache(self, instance, descriptors):
        """
        Helper: set an instance's descriptor cache.
        """
        setattr(instance, '_%s_cache' % self.attname, descriptors)

    def _update_instance_descriptor_cache(self, instance):
        """
        Helper: update an instance's descriptor cache from actual descriptors.
        """
        # for an unsaved object, leave the default value alone
        if instance.pk is not None:
            descriptors = edit_string_for_descriptors(Descriptor.objects.get_for_object(instance))
            described_items = DescribedItem.objects.filter(object_id=instance.id)
            descriptors = [[di.id, di.value] for di in described_items]
            descriptors_json = simplejson.dumps(descriptors,
                                                ensure_ascii=False)
            self._set_instance_descriptors_cache(instance, descriptors_json)

    def get_internal_type(self):
        return 'CharField'

    def formfield(self, **kwargs):
        from descriptors import forms
        defaults = {'form_class': forms.DescriptorField}
        defaults.update(kwargs)
        return super(DescriptorField, self).formfield(**defaults)

