#!/bin/bash

set -e

pip install pytest-cov genbadge[coverage]
pip install --src /openedx/venv/src -e /openedx/requirements/app

cd /openedx/requirements/app

# test uchileedxlogin
echo 'TESTING WITH uchileedxlogin'
pip install --src /openedx/venv/src -e git+https://github.com/eol-uchile/uchileedxlogin@0.0.1#egg=uchileedxlogin
mkdir -p test_root
ln -s /openedx/staticfiles ./test_root/
DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest sence/tests.py
rm -rf test_root
pip uninstall uchileedxlogin
rm -Rfv /openedx/venv/src/uchileedxlogin

# test eol_sso_login
echo 'TESTING WITH eol_sso_login'
pip install --src /openedx/venv/src -e git+https://github.com/eol-uchile/eol_sso_login@0.1.1#egg=eol_sso_login
mkdir -p test_root
ln -s /openedx/staticfiles ./test_root/
DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest sence/tests.py
rm -rf test_root

genbadge coverage
