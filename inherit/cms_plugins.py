from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template.context import Context
from django.conf import settings
from cms.models import CMSPlugin
from models import InheritPagePlaceholder
from django.template.context import Context
from django.conf import settings

class InheritPagePlaceholderPlugin(CMSPluginBase):
    model = InheritPagePlaceholder
    name = _("Inherit Plugins from Parent Page")
    render_template = "cms/plugins/inherit_plugins.html"

    def render(self, context, instance, placeholder):
        template_vars = {
            'placeholder': placeholder,
        }
        template_vars['object'] = instance
        # locate the plugins assigned to the given page for the indicated placeholder
        lang = None
        if context.has_key('request'):
            lang = context['request'].LANGUAGE_CODE
        else:
            lang = settings.LANGUAGE_CODE
        #print 'language CONTEXT FOR PLUGIN:', lang
        plugins = CMSPlugin.objects.filter(page=instance.parent_page, placeholder=placeholder, language=lang)
        plugin_output = []
        template_vars['parent_plugins'] = plugins 
        for plg in plugins:
            #print 'added a parent plugin:', plg, plg.__class__
            # use a temporary context to prevent plugins from overwriting context
            tmpctx = Context()
            tmpctx.update(template_vars)
            inst, name = plg.get_plugin_instance()
            #print 'got a plugin instance:', inst
            outstr = inst.render_plugin(tmpctx, placeholder)
            plugin_output.append(outstr)
            #print 'render result:', outstr
        template_vars['parent_output'] = plugin_output
        context.update(template_vars)
        return context


plugin_pool.register_plugin(InheritPagePlaceholderPlugin)