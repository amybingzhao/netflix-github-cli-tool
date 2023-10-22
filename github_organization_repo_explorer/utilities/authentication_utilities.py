import os
from dotenv import get_key, set_key

DOTENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
PERSONAL_ACCESS_TOKEN_KEY = "GITHUB_PERSONAL_ACCESS_TOKEN"

def get_personal_access_token():
    personal_access_token = get_key(DOTENV_PATH, PERSONAL_ACCESS_TOKEN_KEY)
    if personal_access_token is not None:
        return personal_access_token
    else:
        personal_access_token = _prompt_for_personal_access_token()
        if personal_access_token is not None:
            set_key(DOTENV_PATH, PERSONAL_ACCESS_TOKEN_KEY, personal_access_token)
        return personal_access_token


def _prompt_for_personal_access_token() -> str | None:
    should_use_personal_access_token = input("We could not find a Github personal access token in the .env file. Without one, you may not be able to request certain information and you have a lower limit for requests per hour. Do you want to add one? (y/n): ")
    if should_use_personal_access_token == "y":
        personal_access_token = input("Please enter your personal access token (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens): ")
        return personal_access_token
    elif should_use_personal_access_token == "n":
        return None
    else:
        return _prompt_for_personal_access_token()