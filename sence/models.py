# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from opaque_keys.edx.django.models import CourseKeyField

from datetime import datetime, timedelta

LINE_CHOICES = (
    (1, "Sistema Integrado de Capacitacion"),
    (3, "Impulsa Personas")
)


def expire_datetime():
    """
        Return a expire time of 6 hours by default
    """
    EXPIRE_TIME = getattr(settings, 'SENCE_EXPIRE_TIME', 6)
    return datetime.now() + timedelta(hours=EXPIRE_TIME)


class EolSenceCourseSetup(models.Model):
    """
        Model with Sence Course Setup
    """
    course = CourseKeyField(
        max_length=50,
        unique=True,
        blank=False,
        null=False)
    sence_code = models.CharField(max_length=10, blank=False, null=False)
    sence_course_code = models.CharField(
        max_length=50, blank=False, null=False)
    sence_line = models.IntegerField(
        choices=LINE_CHOICES, blank=False, null=False)


class EolSenceStudentStatus(models.Model):
    """
        Model with Student status
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sence_user")
    course = CourseKeyField(max_length=50, blank=False, null=False)
    id_session = models.CharField(max_length=149, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=expire_datetime)
