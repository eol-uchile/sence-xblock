# -*- coding: utf-8 -*-
# Python Standard Libraries
import logging
logger = logging.getLogger(__name__)

# Installed packages (via pip)
from django.apps import apps
if apps.is_installed('uchileedxlogin'):
    logger.debug('uchileedxlogin activated')
    from uchileedxlogin.services.interface import get_doc_id_by_user_id
    from uchileedxlogin.services.utils import get_document_type
    MODEL_USED = 'uchileedxlogin'
elif apps.is_installed('eol_sso_login'):
    logger.debug('eol_sso_login activated')
    from eol_sso_login.models import SSOLoginExtraData as LoginUserModel
    MODEL_USED = 'eol_sso_login'
else:
    raise ImportError(f"You must have either uchileedxlogin or eol_sso_login installed")

def _format_document_id(document_id, doc_type='rut'):
    """
        Format document_id to Sence requeriments (example: 12345689-0)
    """
    if doc_type == 'rut':
        aux = document_id.lstrip('0')  # remove '0' from the left
        return "{}-{}".format(aux[:-1], aux[-1:])  # add '-' before last digit
    else:
        return document_id

# public methods

def get_user_document_id_and_type(user):
    """
        Get user Document ID if exists
    """
    try:
        if MODEL_USED == 'uchileedxlogin':
            doc_id = get_doc_id_by_user_id(user.id)
            if doc_id is not None:
                document_type = get_document_type(doc_id)
                formatted_doc_id = _format_document_id(doc_id, document_type)
                return formatted_doc_id, document_type
            else:
                return None, None
        else:
            login_obj = LoginUserModel.objects.get(user=user)
            document_id, document_type = login_obj.document, login_obj.type_document
            return _format_document_id(document_id, doc_type=document_type), document_type
    except:
            logger.warning("{} doesn't have a Document ID".format(user.username))
            return None, None
