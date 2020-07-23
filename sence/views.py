# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

from django.contrib.auth.models import User
from uchileedxlogin.models import EdxLoginUser
from opaque_keys.edx.keys import UsageKey

from .models import EolSenceCourseSetup

import logging
logger = logging.getLogger(__name__)



def login_sence(request, block_id):
    """
        GET REQUEST
        RETURN JSON WITH DATA REQUIRED FOR LOGIN
    """
    # check method and params
    if request.method != "GET":
        return HttpResponse(status=400)

    # Get Platform Configuration
    platform_configuration = get_platform_configurations()
    if 'error' in platform_configuration:
        return JsonResponse(status=400, data=platform_configuration)
    rut_otec, sense_token, sense_api_url = platform_configuration

    # Get Course Setup
    course_id = 'course-v1:eol+eol101+2020_1'
    course_setup = get_course_setup(course_id)
    if 'error' in course_setup:
        return JsonResponse(status=400, data=course_setup)
    sense_code, sense_line = course_setup

    # Get User Data
    user = request.user
    user_run = get_user_run(user)

    # Generate URL's
    login_url = "{}Registro/IniciarSesion".format(sense_api_url)
    url_success = request.build_absolute_uri(reverse('login_sence_success'))
    url_fail = request.build_absolute_uri(reverse('login_sence_fail'))

    # Return Data
    data = {
        'login_url'         : login_url,
        'RutOtec'           : rut_otec,
        'Token'             : sense_token,
        'CodSence'          : "-1", # Testing purpose. TODO: EDIT IN PRODUCTION
        'CodigoCurso'       : "-1", # Testing purpose. TODO: EDIT IN PRODUCTION
        'LineaCapacitacion' : sense_line,
        'RunAlumno'         : user_run,
        'IdSesionAlumno'    : block_id,
        'UrlRetoma'         : url_success,
        'UrlError'          : url_fail
    }
    return JsonResponse(data)

@csrf_exempt
def login_sence_success(request):
    """
        Success Login
    """
    if request.method != "POST" or 'IdSesionAlumno' not in request.POST or 'IdSesionSence' not in request.POST:
        return HttpResponse(status=400)
    location = request.POST['IdSesionAlumno']
    usage_key = UsageKey.from_string(location)
    return HttpResponseRedirect(reverse('jump_to', kwargs={'course_id':usage_key.course_key, 'location':location}))

@csrf_exempt
def login_sence_fail(request):
    """
        Fail Login. Render a page with a redirect timeout
    """
    if request.method != "POST" or 'GlosaError' not in request.POST or 'IdSesionAlumno' not in request.POST:
        return HttpResponse(status=400)
    logger.warning('Login Sence Fail {}'.format(request.POST['GlosaError']))
    location = request.POST['IdSesionAlumno']
    usage_key = UsageKey.from_string(location)
    context = {
        'message'   : '[ERROR] Inicio de sesión fallido. Código de error: {}'.format(request.POST['GlosaError']),
        'url'       : reverse('jump_to', kwargs={'course_id':usage_key.course_key, 'location':location})
    }
    return render(request, 'sence/error.html', context)

def get_platform_configurations():
    """
        Get platform configuration or global configuration
    """
    rut_otec = configuration_helpers.get_value('SENCE_RUT_OTEC', settings.SENCE_RUT_OTEC)
    sense_token = configuration_helpers.get_value('SENCE_TOKEN', settings.SENCE_TOKEN)
    sense_api_url = configuration_helpers.get_value('SENCE_API_URL', settings.SENCE_API_URL)
    if rut_otec == '' or sense_token == '' or sense_api_url == '' or rut_otec == {} or sense_token == {} or sense_api_url == {}:
        logger.error('Platform not configurated correctly')
        return {
            'error': 'Platform not configurated correctly'
        }
    return (
        rut_otec,
        sense_token,
        sense_api_url
    )

def get_course_setup(course_id):
    """
        Get course setup (from django admin)
    """
    try:
        setup = EolSenceCourseSetup.objects.get(
            course=course_id
        )
        return (
            setup.sense_code,
            setup.sense_line
        )
    except EolSenceCourseSetup.DoesNotExist:
        logger.error('Course without setup')
        return {
            'error': 'Course without setup'
        }

def get_user_run(user):
    """
        Get user RUN if exists
    """
    try:
        edx_user = EdxLoginUser.objects.get(user=user)
        return format_run(edx_user.run)
    except EdxLoginUser.DoesNotExist:
        logger.warning("{} doesn't have RUN".format(user.username))
        return ''

def format_run(run):
    """
        Format RUN to Sence requeriments (example: 12345689-0)
    """
    aux = run.lstrip('0') # remove '0' from the left
    return "{}-{}".format(aux[:-1], aux[-1:]) # add '-' before last digit