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

from uchileedxlogin.models import EdxLoginUser

from .sence import SenceXBlock

from . import views

import logging
logger = logging.getLogger(__name__)

XBLOCK_RUNTIME_USER_ID = 99


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
            self.assertTrue(self.client.login(username=uname, password=password))

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
        new_run_3= views.format_run(run_3)
        self.assertEqual(new_run_3, '123456-7')

        run_4 = '1234567K'
        new_run_4= views.format_run(run_4)
        self.assertEqual(new_run_4, '1234567-K')

    def test_get_user_run(self):
        """
            Test get user run from uchileedxlogin.
            get_user_run return a sence-formatted run 
        """
        user_run = views.get_user_run(self.user)
        self.assertEqual(user_run, '')

        EdxLoginUser.objects.create(user=self.user, run='00001234567')
        user_run_2 = views.get_user_run(self.user)
        self.assertEqual(user_run_2, '123456-7')


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
            self.assertTrue(self.client.login(username=uname, password=password))

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
