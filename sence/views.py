# -*- coding: utf-8 -*-
# Python Standard Libraries
from __future__ import unicode_literals
from datetime import datetime
from itertools import cycle
import logging
import re

# Installed packages (via pip)
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from eol_sso.services.interface import get_indiv_id
import unicodecsv as csv

# Edx dependencies
from lms.djangoapps.courseware.access import has_access
from opaque_keys.edx.keys import UsageKey
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

# Internal project dependencies
from .models import EolSenceCourseSetup, EolSenceStudentSetup, EolSenceStudentStatus

logger = logging.getLogger(__name__)

def export_attendance(request, block_id):
    """
        Export CSV with students attendance
    """
    usage_key = UsageKey.from_string(block_id)
    course_id = usage_key.course_key
    staff_access = bool(has_access(request.user, 'staff', course_id))
    if not staff_access:
        raise Http404()
    # Getting all students setups and generate a dict with the data
    students_setups = EolSenceStudentSetup.objects.filter(
        course=course_id
    ).values(
        'user_run',
        'sence_course_code'
    )
    students_dict = { student['user_run'] : student['sence_course_code'] for student in students_setups }
    # Getting all students status
    status = EolSenceStudentStatus.objects.filter(
        course=course_id
        ).select_related(
            'user', 'user__profile'
        ).order_by(
            'user__username',
            'created_at'
        )
    # Generate a CSV Response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="SENCE_{}.csv"'.format(
        course_id)
    writer = csv.writer(
        response,
        delimiter=';',
        dialect='excel',
        encoding='utf-8')
    writer.writerow([
        'RUN',
        'Código de Curso',
        'Usuario',
        'Correo Electrónico',
        'Nombre',
        f'Inicio de Sesión (Timezone {settings.TIME_ZONE})'
    ])
    for s in status:
        user_rut = get_formatted_user_rut(s.user)
        writer.writerow([
            user_rut,
            students_dict.get(user_rut, 'undefined'),
            s.user.username,
            s.user.email,
            s.user.profile.name,
            s.created_at.strftime("%d-%m-%Y-%H:%M:%S"),
        ])
    return response


def login_sence(request, block_id):
    """
        GET REQUEST
        RETURN JSON WITH DATA REQUIRED FOR LOGIN
    """
    # check method and params
    if request.method != "GET":
        return JsonResponse(
            status=400,
            data={
                'error': 'method',
                'message': 'Incorrect Request Method'})

    # Get Platform Configuration
    platform_configuration = get_platform_configurations()
    if 'error' in platform_configuration:
        return JsonResponse(
            status=400,
            data={
                'error': 'platform_configuration',
                'message': platform_configuration['error']})
    rut_otec, sence_token, sence_api_url = platform_configuration

    # Get Course Setup
    usage_key = UsageKey.from_string(block_id)
    course_id = usage_key.course_key
    course_setup = get_course_setup(course_id)
    if 'error' in course_setup:
        return JsonResponse(
            status=400,
            data={
                'error': 'course_setup',
                'message': course_setup['error']})
    sence_code, sence_line = course_setup

    # Get User Data
    user = request.user
    user_rut = get_formatted_user_rut(user)
    if not user_rut:
        logger.error(f'User: {user} is trying to log in into sence using a invalid rut')
        return JsonResponse(
            status=400,
            data={
                'error': 'user_doesnt_have_rut',
                'message': 'User doesn\'t have a Chilean RUT'})
    sence_course_code = get_student_sence_course_code(user_rut, course_id)
    if 'error' in sence_course_code:
        return JsonResponse(
            status=400,
            data={
                'error': 'sence_course_code',
                'message': sence_course_code['error']})

    # Generate URL's
    login_url = "{}Registro/IniciarSesion".format(sence_api_url)
    logout_url = "{}Registro/CerrarSesion".format(sence_api_url)
    url_login_success = request.build_absolute_uri(
        reverse('login_sence_success'))
    url_login_fail = request.build_absolute_uri(reverse('login_sence_fail'))
    url_logout_success = request.build_absolute_uri(
        reverse('logout_sence_success'))
    url_logout_fail = request.build_absolute_uri(reverse('logout_sence_fail'))

    # Get user session status
    session_status = get_session_status(user, course_id)

    # Return Data
    data = {
        'login_url': login_url,
        'logout_url': logout_url,
        'RutOtec': rut_otec,
        'Token': sence_token,
        'CodSence': sence_code,
        'CodigoCurso': sence_course_code,
        'LineaCapacitacion': sence_line,
        'RunAlumno': user_rut,
        'IdSesionAlumno': block_id,
        'UrlRetomaLogin': url_login_success,
        'UrlErrorLogin': url_login_fail,
        'UrlRetomaLogout': url_logout_success,
        'UrlErrorLogout': url_logout_fail,
        'session_status': session_status,
    }
    return JsonResponse(data)


@csrf_exempt
def login_sence_success(request):
    """
        Success Login Request. Save the Sence Session ID and Redirect student to the course
    """
    if request.method != "POST" or 'IdSesionAlumno' not in request.POST or 'IdSesionSence' not in request.POST:
        return HttpResponse(status=400)
    location = request.POST['IdSesionAlumno']
    usage_key = UsageKey.from_string(location)
    set_student_status(
        'login',
        request.user,
        usage_key.course_key,
        request.POST['IdSesionSence'])
    return HttpResponseRedirect(
        reverse(
            'jump_to',
            kwargs={
                'course_id': usage_key.course_key,
                'location': location}))


@csrf_exempt
def login_sence_fail(request):
    """
        Fail Login Request. Render a page with a redirect timeout
    """
    if request.method != "POST" or 'GlosaError' not in request.POST or 'IdSesionAlumno' not in request.POST:
        return HttpResponse(status=400)
    logger.warning('Login Sence Fail {}'.format(request.POST['GlosaError']))
    location = request.POST['IdSesionAlumno']
    usage_key = UsageKey.from_string(location)
    context = {
        'message': '[ERROR] Inicio de sesión fallido. Código de error: {}'.format(
            request.POST['GlosaError']), 'url': reverse(
            'jump_to', kwargs={
                'course_id': usage_key.course_key, 'location': location})}
    return render(request, 'sence/error.html', context)


@csrf_exempt
def logout_sence_success(request):
    """
        Success Logout Request
    """
    if request.method != "POST" or 'IdSesionAlumno' not in request.POST:
        return HttpResponse(status=400)
    location = request.POST['IdSesionAlumno']
    usage_key = UsageKey.from_string(location)
    set_student_status(
        'logout',
        request.user,
        usage_key.course_key)
    return HttpResponseRedirect(
        reverse(
            'jump_to',
            kwargs={
                'course_id': usage_key.course_key,
                'location': location}))


@csrf_exempt
def logout_sence_fail(request):
    """
        Fail Logout Request. Render a page with a redirect timeout
    """
    if request.method != "POST" or 'GlosaError' not in request.POST or 'IdSesionAlumno' not in request.POST:
        return HttpResponse(status=400)
    logger.warning('Logout Sence Fail {}'.format(request.POST['GlosaError']))
    location = request.POST['IdSesionAlumno']
    usage_key = UsageKey.from_string(location)
    context = {
        'message': '[ERROR] Cierre de sesión fallido. Código de error: {}'.format(
            request.POST['GlosaError']), 'url': reverse(
            'jump_to', kwargs={
                'course_id': usage_key.course_key, 'location': location})}
    return render(request, 'sence/error.html', context)


def set_student_status(action, user, course_id, id_session=None):
    """
        Associate sence session_id with the user
    """
    if action == 'login':
        student_status = EolSenceStudentStatus.objects.create(
            user=user,
            course=course_id,
            id_session=id_session
        )
    elif action == 'logout':
        try:
            student_status = EolSenceStudentStatus.objects.filter(
                user=user,
                course=course_id
            ).latest('created_at')
            student_status.expires_at = datetime.now()
            student_status.save()
        except EolSenceStudentStatus.DoesNotExist:
            logger.warning('Trying to logout without login')


def get_platform_configurations():
    """
        Get platform configuration or global configuration
    """
    rut_otec = configuration_helpers.get_value(
        'SENCE_RUT_OTEC', settings.SENCE_RUT_OTEC)
    sence_token = configuration_helpers.get_value(
        'SENCE_TOKEN', settings.SENCE_TOKEN)
    sence_api_url = configuration_helpers.get_value(
        'SENCE_API_URL', settings.SENCE_API_URL)
    if rut_otec == '' or sence_token == '' or sence_api_url == '' or rut_otec == {
    } or sence_token == {} or sence_api_url == {}:
        logger.error('Platform not configurated correctly')
        return {
            'error': 'Platform not configurated correctly'
        }
    return (
        rut_otec,
        sence_token.upper(),
        sence_api_url
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
            setup.sence_code,
            setup.sence_line
        )
    except EolSenceCourseSetup.DoesNotExist:
        logger.error('Course without setup')
        return {
            'error': 'Course without setup'
        }


def set_students_codes(students, course_id):
    """
        Set student sence course. Remove students setups if run is not in the list
        students is a list of dictionary [{'user_run' : '12345678-9', 'sence_course_code' : 'sence_course_code'}, ...]
    """
    students_rut = []
    with transaction.atomic():
        for student in students:
            EolSenceStudentSetup.objects.update_or_create(
                user_run=student['user_run'],
                course=course_id,
                defaults={'sence_course_code': student['sence_course_code']}
            )
            students_rut.append(student['user_run'])
        # Remove students setups if run is not in the list
        exclude_setups = EolSenceStudentSetup.objects.filter(
            course=course_id
        ).exclude(
            user_run__in=students_rut
        ).delete()



def get_student_sence_course_code(user, course_id):
    """
        Get Student Sence Course Code
    """
    try:
        student_setup = EolSenceStudentSetup.objects.get(
            user_run=user,
            course=course_id
        )
        return student_setup.sence_course_code
    except EolSenceStudentSetup.DoesNotExist:
        logger.warning('Student without sence course code')
        return {
            'error': 'Student without sence course code'
        }


def get_all_sence_course_codes(course_id):
    """
        Get all Sence course codes associated
    """
    sence_course_codes = EolSenceStudentSetup.objects.filter(
        course=course_id
    ).values_list('sence_course_code', flat=True).distinct()
    return list(sence_course_codes)

def get_all_students_setup(course_id):
    """
        Get all Students Setup
    """
    sence_course_codes = EolSenceStudentSetup.objects.filter(
        course=course_id
    ).values('user_run', 'sence_course_code')
    return sence_course_codes

def get_session_status(user, course_id):
    """
        Get User Status (from django admin)
        Return is_active boolean. This will be False if the session is expired or does not exists
    """
    try:
        status = EolSenceStudentStatus.objects.filter(
            user=user,
            course=course_id
        ).latest('created_at')
        return {
            # now() parameter because can't compare offset-naive and
            # offset-aware datetimes
            'is_active': datetime.now(status.expires_at.tzinfo) < status.expires_at,
            'created_at': status.created_at,
            'id_session': status.id_session
        }
    except EolSenceStudentStatus.DoesNotExist:
        return {
            'is_active': False
        }

def get_formatted_user_rut(user):
    """
        Get sence formatted user rut, if it doesn't have one return None
    """
    indiv_id = get_indiv_id(user.id)
    if not indiv_id:
        return None
    if not validate_rut(indiv_id):
        return None
    return format_rut(indiv_id)

def format_rut(rut):
    """
        Format rut to follow Sence requeriments (example: 12345689-0)
    """
    # remove '0' from the left
    stripped_rut = rut.lstrip('0')
    # add '-' before last digit
    return "{}-{}".format(stripped_rut[:-1], stripped_rut[-1:])

def validate_rut(indiv_id):
    """
        Verify if indiv_id is a rut and has a valid format, returns True in that case.
    """
    indiv_id = indiv_id.upper()
    indiv_id = indiv_id.replace("-", "")
    indiv_id = indiv_id.replace(".", "")
    indiv_id = indiv_id.strip()
    if not re.match(r'^[0-9]+[0-9K]$', indiv_id):
        return False
    aux = indiv_id[:-1]
    dv = indiv_id[-1:]
    revertido = list(map(int, reversed(str(aux))))
    factors = cycle(list(range(2, 8)))
    s = sum(d * f for d, f in zip(revertido, factors))
    res = (-s) % 11
    if str(res) == dv:
        return True
    elif dv == "K" and res == 10:
        return True
    else:
        return False
