from __future__ import absolute_import

from django.conf.urls import url
from django.conf import settings

from .views import export_attendance
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = (
    url(
        r'^sence/export/attendance/(?P<block_id>.*)$',
        staff_member_required(export_attendance),
        name='sence_export_attendance',
    ),
)
