#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import pkg_resources

from django.template import Context, Template

from xblock.core import XBlock
from xblock.fields import Integer, Scope, Boolean, String
from xblock.fragment import Fragment
from xblock.exceptions import JsonHandlerError
from xblockutils.studio_editable import StudioEditableXBlockMixin

# Make '_' a no-op so we can scrape strings
_ = lambda text: text

class SenceXBlock(StudioEditableXBlockMixin, XBlock):

    display_name = String(
        display_name=_("Display Name"),
        help=_("Display name for this module"),
        default="Módulo Sence",
        scope=Scope.settings,
    )

    icon_class = String(
        default="other",
        scope=Scope.settings,
    )

    is_active = Boolean(
        display_name = _("Activar Módulo"),
        help = _("Indica si el módulo está activo o no"),
        default = True,
        scope = Scope.settings,
    )

    editable_fields = ('is_active',)
    has_author_view = True

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def author_view(self, context=None):
        context_html = self.get_context()
        template = self.render_template('static/html/author_view.html', context_html)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/sence.css"))
        return frag

    def student_view(self, context=None):
        """
        The primary view of the SenceXBlock, shown to students
        when viewing courses.
        """
        html_context = self.get_context()
        template = self.render_template('static/html/sence.html', html_context)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/sence.css"))
        frag.add_javascript(self.resource_string("static/js/src/sence.js"))
        settings = {
            'is_active': self.is_active,
            'location': str(self.location).split('@')[-1],
            'is_course_staff': getattr(
                self.xmodule_runtime,
                'user_is_staff',
                False),
        }
        frag.initialize_js('SenceXBlock', json_args=settings)
        return frag

    def get_context(self):
        return {
            'xblock': self,
            'location': str(self.location).split('@')[-1],
            'is_course_staff': getattr(
                self.xmodule_runtime,
                'user_is_staff',
                False),
        }


    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("SenceXBlock",
             """<sence/>
             """),
        ]
