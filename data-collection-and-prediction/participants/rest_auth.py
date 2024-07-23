from rest_framework.authentication import TokenAuthentication
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        print("trying to auth")
        # Call the parent class's authenticate method to check the personal token
        resp = super().authenticate(request)
        print(resp)
        try:
            user, token = resp
        except:
            raise AuthenticationFailed("Could not authenticate.")

        # Check the secret token

        #print(request.META)
        secret_token = request.META.get('HTTP_GREENAITOKEN')
        if secret_token != settings.GREENAI_SECRET:
            raise AuthenticationFailed('Invalid secret token. There needs to be a Header "GreenAiToken", I did not get it or it was wrong.')

        return user, token