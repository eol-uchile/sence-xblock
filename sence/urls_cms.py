from __future__ import absolute_import

from django.conf.urls import url
from django.conf import settings

from .views import export_attendance
from django.contrib import admin

from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(
        r'^sence/export/attendance/(?P<block_id>.*)$',
        login_required(export_attendance),
        name='sence_export_attendance',
    ),
)
