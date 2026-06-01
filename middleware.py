import base64
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin
from django.utils import translation
from django.http import HttpResponse
from constance import config
from django.middleware.cache import FetchFromCacheMiddleware as DjangoFetchFromCacheMiddleware

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
        # First, try to get the language from the request (cookie, session, or headers)
        language = translation.get_language_from_request(request)
        
        # Check if we have a custom cookie set by our JS lang menu
        if 'django_language' in request.COOKIES:
            language = request.COOKIES['django_language']
            
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
        
        if language in mapping:
            language = mapping[language]
            
        # Fallback to the SOPDS configuration if nothing is found
        if not language:
             language = config.SOPDS_LANGUAGE
             
        try:
            translation.activate(language)
        except:
            translation.activate(config.SOPDS_LANGUAGE)
            
        request.LANG = language
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        lang = getattr(request, 'LANG', config.SOPDS_LANGUAGE)
        try:
            translation.activate(lang)
            response['Content-Language'] = translation.get_language()
        except:
            pass
        return response

class FetchFromCacheMiddleware(DjangoFetchFromCacheMiddleware):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        else:
            return super(FetchFromCacheMiddleware, self).process_request(request)
