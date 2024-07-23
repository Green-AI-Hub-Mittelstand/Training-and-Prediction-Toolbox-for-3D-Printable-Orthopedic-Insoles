from django.conf import settings # import the settings file

def is_remote(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'IS_REMOTE': settings.IS_REMOTE}