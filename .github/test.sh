#!/bin/dash

pip install -e git+https://github.com/eol-uchile/uchileedxlogin@8cb702fe18c26b29c0667c660c24ee75a03c9ec9#egg=uchileedxlogin
pip install -e /openedx/requirements/sence-xblock

cd /openedx/requirements/sence-xblock
cp /openedx/edx-platform/setup.cfg .
mkdir test_root
cd test_root/
ln -s /openedx/staticfiles .

cd /openedx/requirements/sence-xblock

DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest sence/tests.py

rm -rf test_root
