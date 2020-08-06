from __future__ import absolute_import

from django.conf.urls import url
from django.conf import settings

from .views import login_sence, login_sence_success, login_sence_fail, logout_sence_success, logout_sence_fail

from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(
        r'^sence/login/parameters/(?P<block_id>.*)$',
        login_required(login_sence),
        name='login_sence',
    ),
    url(
        r'^sence/login/success$',
        login_required(login_sence_success),
        name='login_sence_success',
    ),
    url(
        r'^sence/login/fail$',
        login_required(login_sence_fail),
        name='login_sence_fail',
    ),
    url(
        r'^sence/logout/success$',
        login_required(logout_sence_success),
        name='logout_sence_success',
    ),
    url(
        r'^sence/logout/fail$',
        login_required(logout_sence_fail),
        name='logout_sence_fail',
    ),
)
