import os
import sys
sys.path.append('/sopds')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sopds.settings')
import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from sopds_web_backend.views import SettingsView, SetupWizardView, SetupWriteTestView, SettingsLogView
from constance import config
import json

print("=== VAILIB SETUP & SETTINGS REDESIGN VERIFICATION ===")

# 1. Check if Setup Wizard blocks when superuser exists
superuser_count = User.objects.filter(is_superuser=True).count()
print(f"Current superuser count: {superuser_count}")

# 2. Test SetupWriteTestView
factory = RequestFactory()
request = factory.post('/web/setup/write-test/', data={'path': '/tmp/test_write'})
response = SetupWriteTestView(request)
print(f"SetupWriteTestView status: {response.status_code}")
print(f"SetupWriteTestView response content: {response.content.decode('utf-8')}")

# 3. Test SettingsView access restrictions
request_settings = factory.get('/web/settings/')
class DummyUser:
    is_superuser = False
    is_authenticated = True
request_settings.user = DummyUser()
response_settings_anon = SettingsView(request_settings)
if isinstance(response_settings_anon, HttpResponseForbidden) or response_settings_anon.status_code == 403:
    print("PASS: Accessing settings by non-superuser is Forbidden.")
else:
    print("FAIL: Accessing settings by non-superuser is not Forbidden.")

# 4. Test SettingsView for superuser
admin_user = User.objects.filter(is_superuser=True).first()
created_admin = False
if not admin_user:
    # Temporarily create admin
    admin_user = User.objects.create_superuser(username='vailib_test_admin', email='', password='password')
    created_admin = True
    print("Temporarily created test admin.")
else:
    print(f"Using existing superuser: {admin_user.username}")

request_settings.user = admin_user
response_settings_admin = SettingsView(request_settings)
print(f"SettingsView status for superuser: {response_settings_admin.status_code}")

# Check if new sections (System, Storage, Integrations, Scanner, Logs) are present in the HTML context
html_content = response_settings_admin.content.decode('utf-8')
expected_tabs = ['panel-system', 'panel-storage', 'panel-integrations', 'panel-scanner', 'panel-logs']
for tab in expected_tabs:
    if tab in html_content:
        print(f"PASS: Tab panel id='{tab}' found in settings HTML.")
    else:
        print(f"FAIL: Tab panel id='{tab}' NOT found in settings HTML.")

# 5. Test SettingsLogView
request_logs = factory.get('/web/settings/logs/', data={'type': 'server'})
request_logs.user = admin_user
response_logs = SettingsLogView(request_logs)
print(f"SettingsLogView status: {response_logs.status_code}")
print(f"SettingsLogView content preview: {response_logs.content.decode('utf-8')[:300]}")

if created_admin:
    admin_user.delete()
    print("Deleted temporary test admin.")

print("=== VERIFICATION DONE ===")
