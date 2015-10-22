"""
Platform support for Programs.

This package is a thin wrapper around interactions with the Programs service,
supporting learner- and author-facing features involving that service
if and only if the service is deployed in the Open edX installation.

To ensure maximum separation of concerns, and a minimum of interdependence's,
this package should be kept small, thin, and stateless.
"""

import logging

from django.conf import settings
from django.contrib.auth.models import User

from openedx.core.lib.programs.utils import get_id_token, programs_api_client, is_programs_service_configured


log = logging.getLogger(__name__)


def get_course_programs_for_dashboard(user, course_keys):   # pylint: disable=invalid-name
    """ Given a username and an iterable of course keys, find all
    the programs relevant to the user's dashboard and return them in a
    dictionary keyed by the course_key.

    username is a string coming from the currently-logged-in user's name
    dashboard enrollments is an iterable of course keys

    TODO: ultimately, we will want this function to be versioned, since
    it assumes v1 of the programs API.  This is not critical for our
    initial release.
    """
    # unicode-ify the course keys for efficient lookup
    course_keys = map(unicode, course_keys)

    # get programs slumber-based client 'EdxRestApiClient'
    if not is_programs_service_configured:
        log.error("programs service is not properly configured.")
        return
    try:
        api_client = programs_api_client(settings.PROGRAMS_API_URL, get_id_token(user, 'programs'))
        log.info("Programs slumber-based client 'EdxRestApiClient' created successfully.")
    except ValueError:
        log.error('Failed to create programs api client.', exc_info=True)
        return

    course_programs = {}
    # get programs from api client
    try:
        response = api_client.programs.get()
    except Exception:  # pylint: disable=broad-except
        log.error('Failed to get programs from api client.', exc_info=True)
        return course_programs

    programs = response['results']
    if programs is None:
        log.info("No xseries found for the user '%s'.", user.username)
        return course_programs

    # reindex the result from pgm -> course code -> course run
    #  to
    # course run -> program, ignoring course runs not present in the dashboard enrollments
    course_programs = {}
    for program in programs:
        for course_code in program['course_codes']:
            for run in course_code['run_modes']:
                if run['course_key'] in course_keys:
                    course_programs[run['course_key']] = program

    return course_programs
