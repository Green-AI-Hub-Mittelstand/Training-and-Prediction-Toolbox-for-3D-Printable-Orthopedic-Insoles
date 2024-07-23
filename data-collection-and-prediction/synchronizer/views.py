from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
import os

from participants.decorators import check_auth_and_superuser__token_and_session



# Create your views here.
# View that serves media files only for superusers
@check_auth_and_superuser__token_and_session
def serve_media(request, path):
    # Get the absolute path of the requested media file
    file_path = os.path.join(settings.MEDIA_ROOT, path)

    # Check if the file exists
    if os.path.exists(file_path):
        # Open the file and serve it as an HttpResponse
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
            return response
    else:
        # Return a 404 response if the file is not found
        return HttpResponseNotFound("File not found")