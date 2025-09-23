# -*- coding: utf-8 -*-
# Python Standard Libraries
import logging

# Installed packages (via pip)
from django.test import TestCase
from mock import patch

# Edx dependencies
from student.tests.factories import UserFactory

# Internal project dependencies
from sence.integrations.login_interface import get_user_document_id_and_type

logger = logging.getLogger(__name__)


class LoginInterfaceTests(TestCase):

    def setUp(self):
        # Patch the comment client user save method so it does not try
        # to create a new cc user when creating a django user
        with patch('student.models.cc.User.save'):
            self.user = UserFactory(username='student', email='student@edx.org')

    def test_get_user_without_document_id_uchileedxlogin(self):
        """
            Test get_user_document_id_and_type for a user without a document_id in uchileedxlogin.
        """
        with patch('sence.integrations.login_interface.get_doc_id_by_user_id') as mock_doc_id:
            mock_doc_id.return_value = None
            user_document_id, user_document_type = get_user_document_id_and_type(self.user)
            self.assertEqual(user_document_id, None)
            self.assertEqual(user_document_type, None)

    def test_get_user_with_document_id_uchileedxlogin(self):
        """
            Test get_user_document_id_and_type with a rut type document_id in uchileedxlogin.
        """
        with patch('sence.integrations.login_interface.get_doc_id_by_user_id') as mock_doc_id:
            mock_doc_id.return_value = '001234567K'
            user_document_id, user_document_type = get_user_document_id_and_type(self.user)
            self.assertEqual(user_document_id, '1234567-K')
            self.assertEqual(user_document_type, 'rut')
