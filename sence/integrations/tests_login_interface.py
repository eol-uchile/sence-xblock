# -*- coding: utf-8 -*-
# Python Standard Libraries
import logging

# Installed packages (via pip)
from django.test import TestCase
from mock import Mock, patch
import pytest

# Edx dependencies
from student.tests.factories import UserFactory

# Internal project dependencies
from sence.integrations.login_interface import get_user_document_id_and_type, _format_document_id, MODEL_USED

logger = logging.getLogger(__name__)


class LoginInterfaceTests(TestCase):

    def setUp(self):
        # Patch the comment client user save method so it does not try
        # to create a new cc user when creating a django user
        with patch('student.models.cc.User.save'):
            self.user = UserFactory(username='student', email='student@edx.org')
            self.user2 = UserFactory(username='student2', email='student2@edx.org')

    def test_format_document_id(self):
        """
            Test format document_id (123456-7)
            document_id are in the format: 00123456789
        """
        document_id = '01234567'
        new_document_id = _format_document_id(document_id, doc_type='rut')
        self.assertEqual(new_document_id, '123456-7')

        document_id_2 = '00001234567'
        new_document_id_2 = _format_document_id(document_id_2, doc_type='rut')
        self.assertEqual(new_document_id_2, '123456-7')

        document_id_3 = '1234567'
        new_document_id_3 = _format_document_id(document_id_3, doc_type='rut')
        self.assertEqual(new_document_id_3, '123456-7')

        document_id_4 = '1234567K'
        new_document_id_4 = _format_document_id(document_id_4, doc_type='rut')
        self.assertEqual(new_document_id_4, '1234567-K')

        document_id_5 = '1234567K'
        new_document_id_5 = _format_document_id(document_id_5, doc_type='dni')
        self.assertEqual(new_document_id_5, '1234567K')

        malformed_document_id = '123'
        new_document_id_6 = _format_document_id(malformed_document_id, doc_type='rut')
        self.assertEqual(new_document_id_6, '12-3') 

    def test_get_user_without_document_id_uchileedxlogin(self):
        """
            Test get_user_document_id_and_type for a user without a document_id in uchileedxlogin.
        """
        if MODEL_USED != "uchileedxlogin":
            pytest.skip("Only valid for uchileedxlogin")
        with patch('sence.integrations.login_interface.get_doc_id_by_user_id') as mock_doc_id:
            mock_doc_id.return_value = None
            user_document_id, user_document_type = get_user_document_id_and_type(self.user)
            self.assertEqual(user_document_id, None)
            self.assertEqual(user_document_type, None)

    def test_get_user_with_document_id_uchileedxlogin(self):
        """
            Test get_user_document_id_and_type with a rut type document_id in uchileedxlogin.
        """
        if MODEL_USED != "uchileedxlogin":
            pytest.skip("Only valid for uchileedxlogin")
        with patch('sence.integrations.login_interface.get_doc_id_by_user_id') as mock_doc_id:
            mock_doc_id.return_value = '001234567K'
            user_document_id, user_document_type = get_user_document_id_and_type(self.user)
            self.assertEqual(user_document_id, '1234567-K')
            self.assertEqual(user_document_type, 'rut')

    def test_get_user_document_id_without_doc_id_sso_login(self):
        """
            Test get_user_document_id_and_type for a user without a document_id in eol_sso_login.
            The mock has a side_effect instead of a return_value since in the case of the user not having 
            document_id/extra_data associated with it, the get into the Model is going to raise an exception.
        """
        if MODEL_USED != "eol_sso_login":
            pytest.skip("Only valid for eol_sso_login")
        with patch('eol_sso_login.models.SSOLoginExtraData.objects.get') as mock_get:
            mock_get.side_effect = Exception("User not found")
            user_document_id, user_document_type = get_user_document_id_and_type(self.user)
            self.assertEqual(user_document_id, None)
            self.assertEqual(user_document_type, None)

    def test_get_user_document_id_with_doc_id_sso_login(self):
        """
            Test get_user_document_id_and_type for a user with a document_id, and run document_type
            in eol_sso_login.
        """
        if MODEL_USED != "eol_sso_login":
            pytest.skip("Only valid for eol_sso_login")
        with patch('eol_sso_login.models.SSOLoginExtraData.objects.get') as mock_get:
            mock_login_user = Mock()
            mock_login_user.document = '00001234567'
            mock_login_user.type_document = 'rut'
            mock_get.return_value = mock_login_user
            user_document_id, user_document_type = get_user_document_id_and_type(self.user)
            self.assertEqual(user_document_id, '123456-7')
            self.assertEqual(user_document_type, 'rut')
        
    def test_get_user_document_id_other_type_sso_login(self):
        """
            Test get_user_document_id_and_type for a user with a document_id, and a document_type of dni
            in eol_sso_login.
        """
        if MODEL_USED != "eol_sso_login":
            pytest.skip("Only valid for eol_sso_login")
        with patch('eol_sso_login.models.SSOLoginExtraData.objects.get') as mock_get:
            mock_login_user = Mock()
            mock_login_user.document = '00001234567'
            mock_login_user.type_document = 'dni'
            mock_get.return_value = mock_login_user
            user_document_id, user_document_type = get_user_document_id_and_type(self.user2)
            self.assertEqual(user_document_id, '00001234567')
            self.assertEqual(user_document_type, 'dni')
