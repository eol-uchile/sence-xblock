# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import EolSenceCourseSetup, EolSenceStudentSetup, EolSenceStudentStatus


class EolSenceCourseSetupAdmin(admin.ModelAdmin):
    list_display = ('course', 'sence_code', 'sence_line')

class EolSenceStudentSetupAdmin(admin.ModelAdmin):
    list_display = ('user_run', 'course', 'sence_course_code')

class EolSenceStudentStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at', 'expires_at')


admin.site.register(EolSenceCourseSetup, EolSenceCourseSetupAdmin)
admin.site.register(EolSenceStudentSetup, EolSenceStudentSetupAdmin)
admin.site.register(EolSenceStudentStatus, EolSenceStudentStatusAdmin)
