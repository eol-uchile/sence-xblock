# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import EolSenceCourseSetup, EolSenceStudentStatus

class EolSenceCourseSetupAdmin(admin.ModelAdmin):
    list_display = ('course', 'sense_code', 'sense_line')

class EolSenceStudentStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at', 'expires_at')

admin.site.register(EolSenceCourseSetup, EolSenceCourseSetupAdmin)
admin.site.register(EolSenceStudentStatus, EolSenceStudentStatusAdmin)