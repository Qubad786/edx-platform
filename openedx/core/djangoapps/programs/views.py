"""
Platform support for Programs.

This package is a thin wrapper around interactions with the Programs service,
supporting learner- and author-facing features involving that service
if and only if the service is deployed in the Open edX installation.

To ensure maximum separation of concerns, and a minimum of interdependence's,
this package should be kept small, thin, and stateless.
"""

import logging

from django.core.exceptions import ImproperlyConfigured

from openedx.core.djangoapps.util.helpers import get_id_token
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.programs.utils import programs_api_client


log = logging.getLogger(__name__)
# OAuth2 Client name for programs
CLIENT_NAME = "programs"


def get_course_programs_for_dashboard(user, course_keys):   # pylint: disable=invalid-name
    """ Return all programs related to a user.

    Given a user and an iterable of course keys, find all
    the programs relevant to the user's dashboard and return them in a
    dictionary keyed by the course_key.

    Arguments:
        user (user object): Currently logged-in User for which we need to get
            JWT ID-Token
        course_keys (list): List of course keys in which user is enrolled

    Returns:
        Json response containing programs or None
    """
    if not ProgramsApiConfig.current().is_student_dashboard_enabled:
        log.info("Programs service for student dashboard is disabled.")
        return

    # unicode-ify the course keys for efficient lookup
    course_keys = map(unicode, course_keys)

    # get programs slumber-based client 'EdxRestApiClient'
    try:
        api_client = programs_api_client(ProgramsApiConfig.current().public_api_url, get_id_token(user, CLIENT_NAME))
        log.info("Programs slumber-based client 'EdxRestApiClient' created successfully.")
    except ValueError:
        log.error('Failed to create programs api client.', exc_info=True)
        return
    except ImproperlyConfigured:
        error_msg = "OAuth2 Client with name '{client_name}' is not present in the DB.".format(client_name=CLIENT_NAME)
        log.error(error_msg, exc_info=True)
        return

    course_programs = {}
    # get programs from api client
    try:
        response = api_client.programs.get()
    except Exception:  # pylint: disable=broad-except
        log.error('Failed to get programs from api client.', exc_info=True)
        return course_programs

    programs = response.get('results')
    if programs is None:
        log.info("No programs found for the user '%s'.", user.username)
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
