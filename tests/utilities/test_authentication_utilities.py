import unittest
from unittest.mock import patch

from utilities.authentication_utilities import get_personal_access_token, PERSONAL_ACCESS_TOKEN_KEY

class TestAuthenticationUtilities(unittest.TestCase):
    @patch("utilities.authentication_utilities.get_key")
    def test_get_personal_access_token_if_one_already_exists(self, mock_get_key):
        mocked_key = "cool_access_token123!!&?"
        mock_get_key.return_value = mocked_key
        self.assertEqual(get_personal_access_token(), mocked_key)
    
    @patch("utilities.authentication_utilities.get_key")
    @patch("utilities.authentication_utilities._prompt_for_personal_access_token")
    @patch("utilities.authentication_utilities.set_key")
    @patch("utilities.authentication_utilities.DOTENV_PATH")
    def test_get_personal_access_token_if_user_sets_one_up(self, mock_dotenv_path, mock_set_key, mock_prompt_for_personal_access_token, mock_get_key):
        mock_dotenv_path.return_value = "cool/directory/.env"
        mock_get_key.return_value = None
        mocked_key = "abc123!!!"
        mock_prompt_for_personal_access_token.return_value = mocked_key
        self.assertEqual(get_personal_access_token(), mocked_key)
        mock_set_key.assert_called_once_with(mock_dotenv_path, PERSONAL_ACCESS_TOKEN_KEY, mocked_key)

    @patch("utilities.authentication_utilities.get_key")
    @patch("utilities.authentication_utilities._prompt_for_personal_access_token")
    @patch("utilities.authentication_utilities.set_key")
    def test_get_personal_access_token_if_user_does_not_set_one_up(self, mock_set_key, mock_prompt_for_personal_access_token, mock_get_key):
        mock_get_key.return_value = None
        mock_prompt_for_personal_access_token.return_value = None
        self.assertEqual(get_personal_access_token(), None)
        mock_set_key.assert_not_called()