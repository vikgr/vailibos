with open('/tmp/sopds_custom/middleware.py', 'w', encoding='utf-8') as f:
    f.write('''import base64
from django.http import HttpResponse
from django.contrib import auth
from django.utils import translation
from django.middleware.cache import FetchFromCacheMiddleware as DjangoFetchFromCacheMiddleware
from django.utils.deprecation import MiddlewareMixin

from constance import config

LANGUAGE_SESSION_KEY = '_language'


class BasicAuthMiddleware(object):
    header = "HTTP_AUTHORIZATION"

    def unauthed(self):
        response = HttpResponse("""<html><title>Auth required</title><body>
                                <h1>Authorization Required</h1></body></html>""", content_type="text/html")
        response['WWW-Authenticate'] = 'Basic realm="OPDS"'
        response.status_code = 401
        return response

    def process_request(self, request):
        if not config.SOPDS_AUTH:
            return

        try:
            authentication = request.META[self.header]
        except KeyError:
            return self.unauthed()

        (auth_meth, auth_data) = authentication.split(' ', 1)
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
''')
print("middleware.py written OK")
