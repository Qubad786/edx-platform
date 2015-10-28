"""
Tests for the Programs.
"""

from mock import patch

from provider.oauth2.models import Client

from openedx.core.djangoapps.programs.views import get_course_programs_for_dashboard
from openedx.core.djangoapps.programs.tests.test_models import ProgramsApiBasicTestConfig
from student.tests.factories import AnonymousUserFactory, UserFactory


class TestGetXSeriesPrograms(ProgramsApiBasicTestConfig):
    """
    Tests for the Programs views.
    """

    def setUp(self, **kwargs):  # pylint: disable=unused-argument
        super(TestGetXSeriesPrograms, self).setUp()
        self.create_config(enabled=True, enable_student_dashboard=True)
        Client.objects.get_or_create(name="programs", client_type=0)
        self.user = UserFactory()
        self.programs_api_response = {
            "results": [
                {
                    'category': 'xseries',
                    'status': 'active',
                    'subtitle': 'Dummy program for testing',
                    'name': 'First Program',
                    'course_codes': [
                        {
                            'organization': {'display_name': 'Test Organization', 'key': 'edX'},
                            'display_name': 'Demo Course',
                            'key': 'TEST_A',
                            'run_modes': [{'sku': '', 'mode_slug': 'ABC', 'course_key': 'edX/DemoX/Run'}]
                        }
                    ]
                }
            ]
        }

    def test_get_course_programs_with_valid_user_and_courses(self):
        """ Test that the method 'get_course_programs_for_dashboard' returns
        the expected format.
        """
        # mock the request call
        with patch('slumber.Resource.get') as mock_get:
            mock_get.return_value = self.programs_api_response
            programs = get_course_programs_for_dashboard(self.user, ['edX/DemoX/Run', 'valid/edX/Course'])
            expected_output = {
                'edX/DemoX/Run': {
                    'category': 'xseries',
                    'status': 'active',
                    'course_codes': [
                        {
                            'organization': {'display_name': 'Test Organization', 'key': 'edX'},
                            'display_name': 'Demo Course',
                            'key': 'TEST_A',
                            'run_modes': [{'sku': '', 'mode_slug': 'ABC', 'course_key': 'edX/DemoX/Run'}]
                        }
                    ],
                    'subtitle': 'Dummy program for testing',
                    'name': 'First Program'
                }
            }
            self.assertEqual(expected_output, programs)

    def test_get_course_programs_with_non_existing_courses(self):
        """ Test that the method 'get_course_programs_for_dashboard' returns
        only those program courses which exists in the programs api response.
        """
        # mock the request call
        with patch('slumber.Resource.get') as mock_get:
            mock_get.return_value = self.programs_api_response
            self.assertEqual(
                get_course_programs_for_dashboard(self.user, ['invalid/edX/Course']), {}
            )

    def test_get_course_programs_with_invalid_user(self):
        """ Test that the method 'get_course_programs_for_dashboard' returns
        None for an anonymous user.
        """
        # mock the request call
        with patch('slumber.Resource.get') as mock_get:
            mock_get.return_value = self.programs_api_response
            self.assertIsNone(get_course_programs_for_dashboard(AnonymousUserFactory(), ['edX/DemoX/Run']))

    def test_get_course_programs_with_empty_response(self):
        """ Test that the method 'get_course_programs_for_dashboard' returns
        empty dict if programs rest api client returns empty response.
        """
        # mock the request call
        with patch('slumber.Resource.get') as mock_get:
            mock_get.return_value = {}
            self.assertEqual(
                get_course_programs_for_dashboard(self.user, ['edX/DemoX/Run']), {}
            )
