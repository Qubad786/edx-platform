"""
Tests for the Programs.
"""

import json
from mock import patch, Mock

from django.test import TestCase
from openedx.core.lib.programs import get_course_programs_for_dashboard
from provider.oauth2.models import Client
from student.tests.factories import UserFactory


class TestGetXSeriesProgram(TestCase):
    """Basic tests for programs."""

    def setUp(self, **kwargs):  # pylint: disable=unused-argument
        super(TestGetXSeriesProgram, self).setUp()
        Client.objects.get_or_create(name="programs", client_type=0)
        self.user = UserFactory()
        self.response = json.dumps(
            {
                "results": [
                    {"course_codes": [{"run_modes": [{"course_key": "edx/demox/course"}, {"course_key": "a/c/c"}]}]},
                    {"course_codes": [{"run_modes": [{"course_key": "z/c/v"}, {"course_key": "valid/edx/course"}]}]},
                    {"course_codes": [{"run_modes": [{"course_key": "z/z/z"}, {"course_key": "g/h/f"}]}]}
                ]
            }
        )

    def test_get_course_programs_with_valid_user_and_courses(self):
        """Mock the request call. """
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, content=self.response)
            programs = get_course_programs_for_dashboard(self.user.username, ['edx/demox/course', 'valid/edx/course'])
            self.assertDictEqual(
                {
                    'edx/demox/course': {
                        "course_codes": [{"run_modes": [{"course_key": "edx/demox/course"}, {"course_key": "a/c/c"}]}]
                    },
                    'valid/edx/course': {
                        "course_codes": [{"run_modes": [{"course_key": "z/c/v"}, {"course_key": "valid/edx/course"}]}]
                    }
                },
                programs
            )

    def test_get_course_programs_with_non_existing_courses(self):
        """Mock the request call. """
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, content=self.response)
            self.assertDictEqual(
                {},
                get_course_programs_for_dashboard(self.user.username, ['invalid/demo/course'])
            )

    def test_get_course_programs_with_invalid_user(self):
        """Mock the request call. """
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, content=self.response)
            self.assertIsNone(
                get_course_programs_for_dashboard('invalid_user', ['edx/demox/course'])
            )

    def test_get_course_programs_with_empty_response(self):
        """Mock the request call. """
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, content=json.dumps({}))
            self.assertIsNone(
                get_course_programs_for_dashboard(self.user.username, ['edx/demox/course'])
            )
