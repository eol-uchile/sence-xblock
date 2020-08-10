#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pkg_resources

from django.template import Context, Template
from webob import Response

from xblock.core import XBlock
from xblock.fields import Integer, Scope, Boolean, String
from xblock.fragment import Fragment
from xblock.exceptions import JsonHandlerError
from opaque_keys.edx.keys import UsageKey
from six import text_type

from django.urls import reverse

# Make '_' a no-op so we can scrape strings
def _(text): return text


import logging
logger = logging.getLogger(__name__)


class SenceXBlock(XBlock):

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
        context_html['config'] = get_configurations(
            self.xmodule_runtime.course_id)
        context_html['export_attendance_url'] = reverse('sence_export_attendance', kwargs={'block_id': self.location})
        template = self.render_template(
            'static/html/author_view.html', context_html)
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
        location = str(self.location).split('@')[-1]
        settings = {
            'location': location, 'is_course_staff': getattr(
                self.xmodule_runtime, 'user_is_staff', False), 'sence_login': reverse(
                'login_sence', kwargs={
                    'block_id': self.location})}
        frag.initialize_js('SenceXBlock', json_args=settings)
        return frag

    def studio_view(self, context=None):
        context_html = self.get_context()
        usage_key = UsageKey.from_string(text_type(self.scope_ids.usage_id))
        course_id = usage_key.course_key
        context_html['students_setup'] = get_students_setups(course_id)
        template = self.render_template(
            'static/html/studio.html', context_html)
        frag = Fragment(template)
        frag.add_javascript(self.resource_string("static/js/src/studio.js"))
        frag.initialize_js('SenceStudioXBlock')
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

    @XBlock.handler
    def save_students_codes(self, request, suffix=''):
        from .views import set_students_codes
        students_codes = request.params['students_codes'].rstrip("\n")
        students = []
        for student in students_codes.split('\n'):
            student_data = student.split(' ')
            if len(student_data) == 2:
                # RUN WITH '-' AND WITHOUT '.'
                if '-' in student_data[0] and '.' not in student_data[0]:
                    students.append({
                        'user_run' : student_data[0],
                        'sence_course_code' : student_data[1]
                    })
                else:
                    error = '[ERROR] Invalid Format RUN {}'.format(student_data[0])
                    return Response(json={'result': 'error', 'message': error}, status=400)
            else:
                error = '[ERROR] Invalid Line: {}'.format(student)
                return Response(json={'result': 'error', 'message': error}, status=400)
        usage_key = UsageKey.from_string(text_type(self.scope_ids.usage_id))
        course_id = usage_key.course_key
        set_students_codes(students, course_id)
        return Response(json={'result': 'success', 'message': 'hola'}, status=200)

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("SenceXBlock",
             """<sence/>
             """),
        ]


def get_configurations(course_id):
    """
    Get platform and course configurations
    """
    from .views import get_course_setup, get_platform_configurations, get_all_sence_course_codes
    platform_configurations = get_platform_configurations()
    course_setup = get_course_setup(course_id)
    if 'error' in course_setup:
        sence_code = 'undefined'
        sence_line = 'undefined'
    else:
        sence_code, sence_line = course_setup

    sence_course_codes = ', '.join(get_all_sence_course_codes(course_id))
    return {
        'sence_code': sence_code,
        'sence_course_codes': sence_course_codes,
        'sence_line': sence_line
    }

def get_students_setups(course_id):
    """
        Get all the students setups, and return string with the values separated by \n
    """
    from .views import get_all_students_setup
    students = get_all_students_setup(course_id)
    students_text = ''
    for s in students:
        students_text += '{} {}\n'.format(s['user_run'], s['sence_course_code'])
    return students_text