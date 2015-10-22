"""
Helper methods for Programs.
"""

import logging

from django.conf import settings
from edx_rest_api_client.client import EdxRestApiClient
from provider.oauth2.models import AccessToken, Client
from provider.utils import now


log = logging.getLogger(__name__)


def is_programs_service_configured():
    """ Returns a Boolean indicating whether or not configuration is present to
    use the external programs service.
    """
    return bool(settings.PROGRAMS_API_URL)


def programs_api_client(api_url, jwt_access_token):
    """ Returns an Programs API client setup with authentication for the
    specified user.
    """
    return EdxRestApiClient(
        api_url,
        jwt=jwt_access_token
    )


def get_id_token(user, client_name):
    """
    Generates a JWT ID-Token, using or creating user's OAuth access token.

    Returns a string containing the signed JWT value.

    TODO: this closely duplicates the function in edxnotes/helpers.py - we
    should move it to a shared place (and add a client name parameter)

    TODO: there's a circular import problem somewhere which is why we do
    the oidc import inside of this function.
    """
    import oauth2_provider.oidc as oidc  # avoid circular import problem

    try:
        client = Client.objects.get(name=client_name)
    except Client.DoesNotExist:
        log.error("OAuth2 Client with the name 'programs' is not present in the DB.", exc_info=True)
        return

    access_tokens = AccessToken.objects.filter(
        client=client,
        user__username=user.username,
        expires__gt=now()
    ).order_by('-expires')

    if access_tokens:
        access_token = access_tokens[0]
    else:
        access_token = AccessToken(client=client, user=user)
        access_token.save()

    id_token = oidc.id_token(access_token)
    secret = id_token.access_token.client.client_secret
    return id_token.encode(secret)
