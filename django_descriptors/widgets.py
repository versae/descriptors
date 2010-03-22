# -*- coding: utf-8 -*-
from django import get_version
from django.forms import widgets
from django.utils.safestring import mark_safe


class Combobox(widgets.Select):

    class Media:
        css = {
            'all': ('django_descriptors/css/jquery.combobox.css', ),
        }
        js = []
        if int(get_version().split(" ")[0].split(".")[1]) < 2:
            js.append('django_descriptors/js/jquery.js')
        js.append('django_descriptors/js/jquery.combobox.js')
        js.append('django_descriptors/js/combobox.js')

    def render(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        css_class = attrs.get("class", "")
        attrs["class"] = "%s combobox" % css_class
        kwargs["attrs"] = attrs
        output = super(Combobox, self).render(*args, **kwargs)
        return mark_safe(u"""
        <span class="ui-widget">%s</span>
        """ % (output, ))
