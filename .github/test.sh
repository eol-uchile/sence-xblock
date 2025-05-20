#!/bin/bash

set -e

pip install --src /openedx/venv/src -e git+https://github.com/eol-uchile/uchileedxlogin@0.0.1#egg=uchileedxlogin
pip install --src /openedx/venv/src -e /openedx/requirements/app
pip install pytest-cov genbadge[coverage]

cd /openedx/requirements/app

mkdir -p test_root
ln -sfn /openedx/staticfiles ./test_root/

DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest sence/tests.py

rm -rf test_root

pip uninstall -e git+https://github.com/eol-uchile/uchileedxlogin@0.0.1#egg=uchileedxlogin
pip install --src /openedx/venv/src -e git+https://github.com/eol-uchile/eol_sso_login@0.1.1#egg=eol_sso_login
DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest sence/tests.py


genbadge coverage
