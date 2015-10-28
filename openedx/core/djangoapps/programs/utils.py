"""
Helper methods for Programs.
"""
from edx_rest_api_client.client import EdxRestApiClient


def programs_api_client(api_url, jwt_access_token):
    """ Returns an Programs API client setup with authentication for the
    specified user.
    """
    return EdxRestApiClient(
        api_url,
        jwt=jwt_access_token
    )
