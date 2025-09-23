# -*- coding: utf-8 -*-
# Python Standard Libraries
import logging

# Installed packages (via pip)
from django.test import TestCase
from mock import Mock, patch

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
            self.user2 = UserFactory(username='student2', email='student2@edx.org')

    def test_get_user_document_id_without_doc_id_sso_login(self):
        """
            Test get_user_document_id_and_type for a user without a document_id in eol_sso_login.
            The mock has a side_effect instead of a return_value since in the case of the user not having 
            document_id/extra_data associated with it, the get into the Model is going to raise an exception.
        """
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
        with patch('eol_sso_login.models.SSOLoginExtraData.objects.get') as mock_get:
            mock_login_user = Mock()
            mock_login_user.document = '00001234567'
            mock_login_user.type_document = 'dni'
            mock_get.return_value = mock_login_user
            user_document_id, user_document_type = get_user_document_id_and_type(self.user2)
            self.assertEqual(user_document_id, '00001234567')
            self.assertEqual(user_document_type, 'dni')
