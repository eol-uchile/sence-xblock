# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from opaque_keys.edx.django.models import CourseKeyField

LINE_CHOICES = (
    (1, "Sistema Integrado de Capacitacion"),
    (3, "Impulsa Personas")
)

class EolSenceCourseSetup(models.Model):
    """
        Model with Sence Course Setup
    """
    course = CourseKeyField(max_length=50, unique=True, blank=False, null=False)
    sense_code = models.CharField(max_length=10, blank=False, null=False)
    sense_line = models.IntegerField(choices=LINE_CHOICES, blank=False, null=False)