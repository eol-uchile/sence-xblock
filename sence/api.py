
# Internal project dependencies
from .integrations.login_interface import get_user_document_id_and_type

def get_user_rut(user):
    document_id, document_type = get_user_document_id_and_type(user)
    if document_type == 'rut':
        return document_id
    else:
        return None
