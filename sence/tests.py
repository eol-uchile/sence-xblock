# -*- coding: utf-8 -*-
from mock import patch, Mock

import json

from django.test import TestCase, Client
from django.urls import reverse

from util.testing import UrlResetMixin
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from xmodule.modulestore.tests.factories import CourseFactory
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from xblock.field_data import DictFieldData
from student.roles import CourseStaffRole
from opaque_keys.edx.keys import UsageKey

from openedx.core.djangoapps.site_configuration.tests.test_util import (
    with_site_configuration,
    with_site_configuration_context,
)

from uchileedxlogin.models import EdxLoginUser

from .sence import SenceXBlock, get_configurations
from . import views
from .models import EolSenceStudentStatus, EolSenceStudentSetup, EolSenceCourseSetup

from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)

XBLOCK_RUNTIME_USER_ID = 99

test_config = {
    'SENCE_RUT_OTEC': 'SENCE_RUT_OTEC',
    'SENCE_TOKEN': 'SENCE_TOKEN',
    'SENCE_API_URL': 'SENCE_API_URL/'
}


class TestRequest(object):
    # pylint: disable=too-few-public-methods
    """
    Module helper for @json_handler
    """
    method = None
    body = None
    success = None
    params = None


class TestSenceAPI(UrlResetMixin, ModuleStoreTestCase):
    def setUp(self):

        super(TestSenceAPI, self).setUp()

        # create a course
        self.course = CourseFactory.create(org='mss', course='999',
                                           display_name='sence tests')

        # Patch the comment client user save method so it does not try
        # to create a new cc user when creating a django user
        with patch('student.models.cc.User.save'):
            uname = 'student'
            email = 'student@edx.org'
            password = 'test'

            # Create the user
            self.user = UserFactory(
                username=uname, password=password, email=email)
            CourseEnrollmentFactory(
                user=self.user,
                course_id=self.course.id)

            # Log the user in
            self.client = Client()
            self.assertTrue(
                self.client.login(
                    username=uname,
                    password=password))

    def test_format_run(self):
        """
            Test format run to sence requirements (123456-7)
            Run from uchileedxlogin are in the format: 00123456789
        """
        run = '01234567'
        new_run = views.format_run(run)
        self.assertEqual(new_run, '123456-7')

        run_2 = '00001234567'
        new_run_2 = views.format_run(run_2)
        self.assertEqual(new_run_2, '123456-7')

        run_3 = '1234567'
        new_run_3 = views.format_run(run_3)
        self.assertEqual(new_run_3, '123456-7')

        run_4 = '1234567K'
        new_run_4 = views.format_run(run_4)
        self.assertEqual(new_run_4, '1234567-K')

    def test_get_user_run(self):
        """
            Test get user run from uchileedxlogin.
            get_user_run return a sence-formatted run
            1. With run
            2. Without run
        """
        user_run = views.get_user_run(self.user)
        self.assertEqual(user_run, '')

        EdxLoginUser.objects.create(user=self.user, run='00001234567')
        user_run_2 = views.get_user_run(self.user)
        self.assertEqual(user_run_2, '123456-7')

    def test_get_session_status(self):
        """
            Test get user status
            1. Without Status
            2. With Status Active
            3. With Status Inactive (expired)
        """
        user_status = views.get_session_status(self.user, self.course.id)
        self.assertEqual(user_status['is_active'], False)

        EolSenceStudentStatus.objects.create(
            user=self.user,
            course=self.course.id,
            id_session='id_session'
        )
        user_status = views.get_session_status(self.user, self.course.id)
        self.assertEqual(user_status['is_active'], True)

        EolSenceStudentStatus.objects.create(
            user=self.user,
            course=self.course.id,
            id_session='id_session',
            expires_at=(datetime.now() - timedelta(hours=2))
        )
        user_status = views.get_session_status(self.user, self.course.id)
        self.assertEqual(user_status['is_active'], False)

    def test_get_all_sence_course_codes(self):
        """
            Test get all the sence_course_codes in a course
            1. Without course_codes
            2. With 1
            3. With 1+
        """
        sence_course_codes_1 = views.get_all_sence_course_codes(self.course.id)
        self.assertEqual(len(sence_course_codes_1), 0)

        EolSenceStudentSetup.objects.create(
            user_run='1234567-8',
            course=self.course.id,
            sence_course_code='code_1'
        )
        EolSenceStudentSetup.objects.create(
            user_run='323213-3',
            course=self.course.id,
            sence_course_code='code_1'
        )
        sence_course_codes_2 = views.get_all_sence_course_codes(self.course.id)
        self.assertEqual(len(sence_course_codes_2), 1)

        EolSenceStudentSetup.objects.create(
            user_run='1234567-9',
            course=self.course.id,
            sence_course_code='code_2'
        )
        sence_course_codes_3 = views.get_all_sence_course_codes(self.course.id)
        self.assertEqual(len(sence_course_codes_3), 2)

    def test_get_student_sence_course_code(self):
        """
            Test get a student sence_course_code
            1. Without code
            1. With code
        """
        sence_course_code = views.get_student_sence_course_code(
            '1234567-9', self.course.id)
        self.assertEqual(
            sence_course_code, {
                'error': 'Student without sence course code'})

        EolSenceStudentSetup.objects.create(
            user_run='1234567-9',
            course=self.course.id,
            sence_course_code='code'
        )
        sence_course_code = views.get_student_sence_course_code(
            '1234567-9', self.course.id)
        self.assertEqual(sence_course_code, 'code')

    def test_get_course_setup(self):
        """
            Test getting course setup
        """
        course_setup = views.get_course_setup(self.course.id)
        self.assertEqual(course_setup, {'error': 'Course without setup'})

        EolSenceCourseSetup.objects.create(
            course=self.course.id,
            sence_code='sence_code',
            sence_line=3
        )
        sence_code, sence_line = views.get_course_setup(self.course.id)
        self.assertEqual(sence_code, 'sence_code')
        self.assertEqual(sence_line, 3)

    def test_get_platform_configurations_1(self):
        """
            Test get platform configuration *without* configurations
        """
        configs = views.get_platform_configurations()
        self.assertEqual(
            configs, {
                'error': 'Platform not configurated correctly'})

    @with_site_configuration(configuration=test_config)
    def test_get_platform_configurations_2(self):
        """
            Test get platform configuration *with* configurations
        """
        rut_otec, sence_token, sence_api_url = views.get_platform_configurations()
        self.assertEqual(rut_otec, 'SENCE_RUT_OTEC')
        self.assertEqual(sence_token, 'SENCE_TOKEN')
        self.assertEqual(sence_api_url, 'SENCE_API_URL/')

    def test_set_student_status(self):
        """
            Test set student status.
            Test created_at and expires_at consistency
        """
        views.set_student_status(self.user, self.course.id, 'id_session')
        status = EolSenceStudentStatus.objects.filter(
            user=self.user,
            course=self.course.id
        ).latest('created_at')
        self.assertEqual(status.id_session, 'id_session')
        self.assertEqual(status.created_at < status.expires_at, True)

    def test_login_sence_fail(self):
        """
            Test Login Sence Fail (POST Request)
            1. GET Request
            2. POST Request without data
            3. Correct POST Request
        """
        response = self.client.get(reverse('login_sence_fail'))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('login_sence_fail'))
        self.assertEqual(response.status_code, 400)

        data = {
            'GlosaError': 'GlosaError',
            'IdSesionAlumno': 'block-v1:eol+eol101+2020_1+type@sence+block@0f6943f9f6cc4f21b9cc878725c6d2cd'
        }
        response = self.client.post(reverse('login_sence_fail'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Espere un momento mientras se redirecciona nuevamente al curso',
            response.content)
        self.assertIn(b'GlosaError', response.content)
        self.assertIn(b'class="error_sence"', response.content)

    def test_login_sence_success(self):
        """
            Test Login Sence Success (POST Request)
            1. GET Request
            2. POST Request without data
            3. Correct POST Request
        """
        response = self.client.get(reverse('login_sence_success'))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('login_sence_success'))
        self.assertEqual(response.status_code, 400)

        data = {
            'IdSesionSence': 'IdSesionSence',
            'IdSesionAlumno': 'block-v1:eol+eol101+2020_1+type@sence+block@0f6943f9f6cc4f21b9cc878725c6d2cd'
        }
        response = self.client.post(reverse('login_sence_success'), data=data)
        self.assertEqual(response.status_code, 302)  # Redirect

    @with_site_configuration(configuration=test_config)
    def test_login_sence(self):
        """
            Test Login Sence (GET Request)
            1. POST Request
            2. GET Request without course setup
            3. GET Request without sence course code
            4. GET Request without active session
            5. GET Request with active session
        """
        # 1
        block_id = 'block-v1:eol+eol101+2020_1+type@sence+block@0f6943f9f6cc4f21b9cc878725c6d2cd'
        response = self.client.post(
            reverse(
                'login_sence', kwargs={
                    'block_id': block_id}))
        self.assertEqual(response.status_code, 400)

        # 2
        response = self.client.get(
            reverse(
                'login_sence', kwargs={
                    'block_id': block_id}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {
                "message": "Course without setup", "error": "course_setup"})

        # 3
        usage_key = UsageKey.from_string(block_id)
        course_id = usage_key.course_key
        EolSenceCourseSetup.objects.create(
            course=course_id,
            sence_code='sence_code',
            sence_line=3
        )
        response = self.client.get(
            reverse(
                'login_sence', kwargs={
                    'block_id': block_id}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                         {'error': 'sence_course_code',
                          'message': 'Student without sence course code'})

        # 4
        EdxLoginUser.objects.create(user=self.user, run='000012345678')
        EolSenceStudentSetup.objects.create(
            user_run='1234567-8',
            course=course_id,
            sence_course_code='code_1'
        )
        correct_response = {
            'CodSence': 'sence_code',
            'CodigoCurso': 'code_1',
            'IdSesionAlumno': 'block-v1:eol+eol101+2020_1+type@sence+block@0f6943f9f6cc4f21b9cc878725c6d2cd',
            'LineaCapacitacion': 3,
            'RunAlumno': '1234567-8',
            'RutOtec': 'SENCE_RUT_OTEC',
            'Token': 'SENCE_TOKEN',
            'UrlError': 'http://testserver/sence/login/fail',
            'UrlRetoma': 'http://testserver/sence/login/success',
            'login_url': 'SENCE_API_URL/Registro/IniciarSesion',
            'session_status': {
                'is_active': False}}
        response = self.client.get(
            reverse(
                'login_sence', kwargs={
                    'block_id': block_id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), correct_response)

        # 5
        status = EolSenceStudentStatus.objects.create(
            user=self.user,
            course=course_id,
            id_session='id_session'
        )
        response = self.client.get(
            reverse(
                'login_sence', kwargs={
                    'block_id': block_id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['session_status']['is_active'], True)


class TestSenceXBlock(UrlResetMixin, ModuleStoreTestCase):

    def make_an_xblock(self, **kw):
        """
        Helper method that creates a Sence XBlock
        """
        course = self.course
        runtime = Mock(
            course_id=course.id,
            user_is_staff=False,
            service=Mock(
                return_value=Mock(_catalog={}),
            ),
            user_id=XBLOCK_RUNTIME_USER_ID,
        )
        scope_ids = Mock()
        field_data = DictFieldData(kw)
        xblock = SenceXBlock(runtime, field_data, scope_ids)
        xblock.xmodule_runtime = runtime
        xblock.location = course.id  # Example of location
        return xblock

    def setUp(self):

        super(TestSenceXBlock, self).setUp()

        # create a course
        self.course = CourseFactory.create(org='mss', course='999',
                                           display_name='sence tests')

        # create sence Xblock
        self.xblock = self.make_an_xblock()
        # Patch the comment client user save method so it does not try
        # to create a new cc user when creating a django user
        with patch('student.models.cc.User.save'):
            uname = 'student'
            email = 'student@edx.org'
            password = 'test'

            # Create and enroll student
            self.student = UserFactory(
                username=uname, password=password, email=email)
            CourseEnrollmentFactory(
                user=self.student, course_id=self.course.id)

            # Create and Enroll staff user
            self.staff_user = UserFactory(
                username='staff_user',
                password='test',
                email='staff@edx.org',
                is_staff=True)
            CourseEnrollmentFactory(
                user=self.staff_user,
                course_id=self.course.id)
            CourseStaffRole(self.course.id).add_users(self.staff_user)

            # Log the student in
            self.client = Client()
            self.assertTrue(
                self.client.login(
                    username=uname,
                    password=password))

            # Log the user staff in
            self.staff_client = Client()
            self.assertTrue(
                self.staff_client.login(
                    username='staff_user',
                    password='test'))

    def test_workbench_scenarios(self):
        """
            Checks workbench scenarios title and basic scenario
        """
        result_title = 'SenceXBlock'
        basic_scenario = "<sence/>"
        test_result = self.xblock.workbench_scenarios()
        self.assertEqual(result_title, test_result[0][0])
        self.assertIn(basic_scenario, test_result[0][1])

    def test_author_view_render(self):
        """
            Check if author view is rendering
        """
        author_view = self.xblock.author_view()
        author_view_html = author_view.content
        self.assertIn('class="sence_author_block"', author_view_html)

    def test_student_view_render(self):
        """
            Check if student view is rendering
        """
        student_view = self.xblock.student_view()
        student_view_html = student_view.content
        self.assertIn('class="sence_block', student_view_html)
        self.assertIn(
            '<form id="login_sence" action="" method="POST">',
            student_view_html)

    def test_studio_view_render(self):
        """
            Check if studio view (Edit) is rendering
        """
        studio_view = self.xblock.studio_view()
        studio_view_html = studio_view.content
        self.assertIn('id="settings-tab"', studio_view_html)

    def test_get_configurations(self):
        """
            Test get configurations
            1. Without course/student setup
            2. With one sence_course_code
            3. With two sence_course_code
        """
        configs = get_configurations(self.course.id)
        self.assertEqual(configs,
                         {'sence_line': 'undefined',
                          'sence_code': 'undefined',
                          'sence_course_codes': ''})

        EolSenceCourseSetup.objects.create(
            course=self.course.id,
            sence_code='sence_code',
            sence_line=3
        )
        EolSenceStudentSetup.objects.create(
            user_run='1234567-8',
            course=self.course.id,
            sence_course_code='code_1'
        )
        configs = get_configurations(self.course.id)
        self.assertEqual(configs,
                         {'sence_line': 3,
                          'sence_code': 'sence_code',
                          'sence_course_codes': 'code_1'})

        EolSenceStudentSetup.objects.create(
            user_run='1234567-K',
            course=self.course.id,
            sence_course_code='code_2'
        )
        configs = get_configurations(self.course.id)
        self.assertEqual(configs,
                         {'sence_line': 3,
                          'sence_code': 'sence_code',
                          'sence_course_codes': 'code_1, code_2'})
