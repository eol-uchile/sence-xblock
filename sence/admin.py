# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import EolSenceCourseSetup

class EolSenceCourseSetupAdmin(admin.ModelAdmin):
    list_display = ('course', 'sense_code', 'sense_line')

admin.site.register(EolSenceCourseSetup, EolSenceCourseSetupAdmin)