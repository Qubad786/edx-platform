"""
Helper methods for Programs.
"""

import logging

from django.conf import settings
from edx_rest_api_client.client import EdxRestApiClient


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
