from __future__ import absolute_import

from django.conf.urls import url
from django.conf import settings

from .views import login_sence

from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(
        r'sence/login',
        login_required(login_sence),
        name='login_sence',
    ),
)