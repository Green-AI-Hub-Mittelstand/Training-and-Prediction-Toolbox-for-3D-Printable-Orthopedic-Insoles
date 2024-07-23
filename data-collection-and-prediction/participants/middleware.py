from django.utils import translation
from django.conf import settings

class LocaleMiddleware:
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context. This allows pages to be dynamically
    translated to the language the user desires (if the language
    is available, of course).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check the session variable for every request
        language = request.session.get("django_language", "de")
        
        print("Language in Session: %s" % language)
        translation.activate(language)
        print("Activating language %s " % language)
        request.LANGUAGE_CODE = language
        response = self.get_response(request)
        translation.deactivate()
        
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response
        