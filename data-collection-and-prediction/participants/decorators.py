from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def admin_required(
    view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="admin:login"
):
    """
    Decorator for views that checks that the user is admin
    member, redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator



from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes, permission_classes
from participants.rest_auth import CustomTokenAuthentication

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User

# Decorator for checking authentication and superuser status
def check_auth_and_superuser(view_func):
    @authentication_classes([CustomTokenAuthentication])
    @permission_classes([IsAuthenticated, IsAdminUser])
    def wrapped_view(request, *args, **kwargs):
        # Check if the request has a valid authentication token
        auth_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]
        try:
            token = Token.objects.get(key=auth_token)
        except Token.DoesNotExist:
            return HttpResponseForbidden("Invalid authentication token")

        # Check if the user associated with the token is a superuser
        user = token.user
        if not user.is_superuser:
            return HttpResponseForbidden("User is not a superuser")

        # Call the original view function if all checks pass
        return view_func(request, *args, **kwargs)

    return wrapped_view


# Decorator for checking authentication and superuser status
def check_auth_and_superuser__token_and_session(view_func):
    @authentication_classes([CustomTokenAuthentication])
    #@permission_classes([IsAuthenticated, IsAdminUser])
    @permission_classes([IsAuthenticated, IsAdminUser])
    def wrapped_view(request, *args, **kwargs):
        # Check if the request has a valid authentication token
        auth_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]

        allowed_to_exec = False
    
        if auth_token != "":  # if an auth header is set, check the token
            try:
                token = Token.objects.get(key=auth_token)
            except Token.DoesNotExist:
                return HttpResponseForbidden("Invalid authentication token")
            else:
                # Check if the user associated with the token is a superuser
                user = token.user
                if not user.is_superuser:
                    return HttpResponseForbidden("User is not a superuser")
                else:
                    allowed_to_exec = True

        if request.user: # this is for the session
            if request.user.is_superuser:
                allowed_to_exec = True


        
        if allowed_to_exec:
            # Call the original view function if all checks pass
            return view_func(request, *args, **kwargs)
        
        else:
            return HttpResponseForbidden("No token sent and no session available. Not authorized.")

    return wrapped_view