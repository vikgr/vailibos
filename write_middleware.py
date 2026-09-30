import os

middleware_code = '''import base64
from django.http import HttpResponse
from django.contrib import auth
from django.utils import translation
from django.middleware.cache import FetchFromCacheMiddleware as DjangoFetchFromCacheMiddleware
from django.utils.deprecation import MiddlewareMixin

from constance import config

LANGUAGE_SESSION_KEY = '_language'


EINK_USER_AGENTS = (
    'kindle', 'kobo', 'nook', 'pocketbook', 'ereader', 'sonyreader', 
    'eink', 'e-ink', 'boox', 'tolino', 'bookeen', 'onyx', 'remarkable',
    'likebook', 'boyue', 'hanvon', 'dasung', 'inkpalm', 'supernote',
    'mobiscribe', 'cybook', 'bokeen', 'inkbook',
    'opera mini', 'symbian', 'blackberry', 'netfront', 'openwave'
)


class VailibThemeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        theme_param = request.GET.get('theme')
        if theme_param in ['eink', 'premium']:
            request.vailib_theme = theme_param
            return

        theme_cookie = request.COOKIES.get('vailib_theme')
        if theme_cookie in ['eink', 'premium']:
            request.vailib_theme = theme_cookie
            return

        # Device detection: check for known e-book readers / e-ink user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(keyword in user_agent for keyword in EINK_USER_AGENTS):
            request.vailib_theme = 'eink'
        else:
            # Modern high-resolution / color display by default (desktop, laptop, tablet, smartphone)
            request.vailib_theme = 'premium'

    def process_response(self, request, response):
        theme_param = request.GET.get('theme')
        if theme_param in ['eink', 'premium']:
            response.set_cookie('vailib_theme', theme_param, max_age=31536000, path='/', samesite='Lax')
        elif hasattr(request, 'vailib_theme'):
            if 'vailib_theme' not in request.COOKIES:
                response.set_cookie('vailib_theme', request.vailib_theme, max_age=31536000, path='/', samesite='Lax')
        return response


class SOPDSSetupMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        # Allow static files, welcome setup wizard views, and login assets
        if path.startswith('/web/setup/') or path.startswith('/static/'):
            return None
            
        # Redirect to welcome setup wizard if database has no superuser
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            from django.shortcuts import redirect
            return redirect('/web/setup/')
        return None


class BasicAuthMiddleware(MiddlewareMixin):
    def unauthed(self):
        response = HttpResponse("""<html><title>Auth required</title><body><h1>401 Unauthorized</h1></body></html>""", status=401)
        response['WWW-Authenticate'] = 'Basic realm="SOPDS"'
        return response

    def process_request(self, request):
        if not config.SOPDS_AUTH:
            return None

        import opds_catalog.utils as utils
        if utils.request_is_opds(request):
            return None

        if 'HTTP_AUTHORIZATION' not in request.META:
            return self.unauthed()

        auth_meth, auth_data = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
        if 'basic' != auth_meth.lower():
            return self.unauthed()
        auth_data = base64.b64decode(auth_data.strip()).decode('utf-8')
        username, password = auth_data.split(':', 1)

        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            request.user = user
            auth.login(request, user)
            return None

        return self.unauthed()


class SOPDSLocaleMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 1. Try cookie (set by our JS flag switcher)
        # 2. Try session
        # 3. Fallback to global config
        lang_cookie = request.COOKIES.get('django_language')
        
        # Support short codes mapping for common ones used in JS switcher
        mapping = {
            'en': 'en-us',
            'zh': 'zh-hans',
            'ru': 'ru',
            'el': 'el',
            'de': 'de',
            'es': 'es',
            'fr': 'fr',
            'ar': 'ar',
            'hi': 'hi',
            'pt': 'pt',
            'bn': 'bn',
            'nl': 'nl',
        }
        
        if lang_cookie in mapping:
            lang = mapping[lang_cookie]
        else:
            lang = lang_cookie or config.SOPDS_LANGUAGE

        request.LANG = lang
        translation.activate(lang)
        request.LANGUAGE_CODE = translation.get_language()
        
        if hasattr(request, 'session'):
            request.session[LANGUAGE_SESSION_KEY] = lang

    def process_response(self, request, response):
        lang = getattr(request, 'LANG', config.SOPDS_LANGUAGE)
        translation.activate(lang)
        response['Content-Language'] = translation.get_language()
        return response


class FetchFromCacheMiddleware(DjangoFetchFromCacheMiddleware):

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        else:
            return super(FetchFromCacheMiddleware, self).process_request(request)
'''

# 1. Write locally to repository root (for Docker build context)
with open('middleware.py', 'w', encoding='utf-8') as f:
    f.write(middleware_code)
print("middleware.py written locally OK")

# 2. Write to fallback /tmp/sopds_custom/middleware.py
try:
    os.makedirs('/tmp/sopds_custom', exist_ok=True)
    with open('/tmp/sopds_custom/middleware.py', 'w', encoding='utf-8') as f:
        f.write(middleware_code)
    print("middleware.py written to /tmp/sopds_custom/ OK")
except Exception as e:
    print(f"Warning: failed to write to /tmp/sopds_custom: {e}")
