# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User

from django.http import HttpResponseRedirect, HttpResponse

import logging
logger = logging.getLogger(__name__)

def login_sence(request):
    """
        GET REQUEST
    """
    # check method and params
    if request.method != "GET":
        return HttpResponse(status=400)

    user = request.user
    logger.warn(user)

    return HttpResponse('<html><body>Ok</body></html>')

