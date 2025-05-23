import logging
from django.apps import apps

logger = logging.getLogger(__name__)
if apps.is_installed('uchileedxlogin'):
    logger.info('uchileedxlogin activated')
    from uchileedxlogin.models import EdxLoginUser as LoginUserModel
    MODEL_USED = 'uchileedxlogin'
elif apps.is_installed('eol_sso_login'):
    logger.info('eol_sso_login activated')
    from eol_sso_login.models import SSOLoginExtraData as LoginUserModel
    MODEL_USED = 'eolssologin'
else:
    raise ImportError(f"You must have either uchileedxlogin or eol_sso_login installed")

LOGIN_FIELD = 'run' if MODEL_USED == 'uchileedxlogin' else 'document'
HAS_TYPE    = any(f.name == 'type' for f in LoginUserModel._meta.get_fields())
DEFAULT_TYPE = 'rut'

def _format_run(run):
    """
        Format RUN to Sence requeriments (example: 12345689-0)
    """
    aux = run.lstrip('0')  # remove '0' from the left
    return "{}-{}".format(aux[:-1], aux[-1:])  # add '-' before last digit

def _raw_run(obj):
    if MODEL_USED == 'uchileedxlogin':
        return obj.run
    else:
        return obj.document
    
def make_login_kwargs(value, type_value=None):
    """
    Build the kwargs for creating a LoginUserModel record:
    """
    kwargs = { LOGIN_FIELD: value }
    if HAS_TYPE:
        kwargs['type'] = type_value or DEFAULT_TYPE
    return kwargs



# public methods
def create_sso_user(user, document_value):
    try:
        LoginUserModel.objects.create(user=user, **make_login_kwargs(document_value))
        return True
    except:
        return False

def get_user_run(user):
    """
        Get user RUN if exists
    """
    try:
        login_obj = LoginUserModel.objects.get(user=user)
        raw = _raw_run(login_obj)
        return _format_run(raw)
    except LoginUserModel.DoesNotExist:
        logger.warning("{} doesn't have RUN".format(user.username))
        return ''

def format_run(run):
    return _format_run(run)
