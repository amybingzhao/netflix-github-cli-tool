import unittest
from unittest.mock import patch

from utilities.cache_utilities import GithubDataCache
from utilities.repo_utilities import get_top_repos_by_criteria
from models.criteria import Criteria
from tests.helpers import create_mock_repository

MOCK_REPO_DATA = {
    "ManyStarsRepo": {
        Criteria.STARS.value: 123,
        Criteria.FORKS.value: 23,
        Criteria.PULL_REQUESTS.value: 12,
    },
    "ManyForksRepo": {
        Criteria.STARS.value: 19,
        Criteria.FORKS.value: 99,
        Criteria.PULL_REQUESTS.value: 5,
    },
    "ManyPullsRepo": {
        Criteria.STARS.value: 0,
        Criteria.FORKS.value: 0,
        Criteria.PULL_REQUESTS.value: 100,
    },
    "ManyContributionsRepo": {
        Criteria.STARS.value: 1,
        Criteria.FORKS.value: 1,
        Criteria.PULL_REQUESTS.value: 99,
    },
}

MOCK_REPOS = [ create_mock_repository("org_name", repo_name) for repo_name in MOCK_REPO_DATA.keys()]

def get_mock_stars_count(repo) -> int:
    return MOCK_REPO_DATA[repo.name][Criteria.STARS.value]

def get_mock_forks_count(repo) -> int:
    return MOCK_REPO_DATA[repo.name][Criteria.FORKS.value]

def get_mock_pull_requests_count(repo) -> int:
    return MOCK_REPO_DATA[repo.name][Criteria.PULL_REQUESTS.value]

class TestRepoUtilities(unittest.TestCase):
    def set_up_mocks(self, mock_get_stars_count, mock_get_forks_count, mock_get_pull_requests_count):
        mock_get_stars_count.side_effect = get_mock_stars_count
        mock_get_forks_count.side_effect = get_mock_forks_count
        mock_get_pull_requests_count.side_effect = get_mock_pull_requests_count

    @patch("utilities.repo_utilities.get_stars_count")
    @patch("utilities.repo_utilities.get_forks_count")
    @patch("utilities.repo_utilities.get_pull_requests_count")
    def test_get_top_repos_by_criteria_with_no_repos(self, mock_get_pull_requests_count, mock_get_forks_count, mock_get_stars_count):
        self.set_up_mocks(mock_get_stars_count, mock_get_forks_count, mock_get_pull_requests_count)
        top_repos = get_top_repos_by_criteria([], n=10, criteria=Criteria.STARS, cache=GithubDataCache())
        self.assertEqual(list(top_repos), [])
    
    @patch("utilities.repo_utilities.get_stars_count")
    @patch("utilities.repo_utilities.get_forks_count")
    @patch("utilities.repo_utilities.get_pull_requests_count")
    def test_get_top_repos_by_criteria_filters_by_requested_criteria_with_fewer_than_n_repos(self, mock_get_pull_requests_count, mock_get_forks_count, mock_get_stars_count):
        self.set_up_mocks(mock_get_stars_count, mock_get_forks_count, mock_get_pull_requests_count)
        top_repos = get_top_repos_by_criteria(MOCK_REPOS, n=10, criteria=Criteria.FORKS, cache=GithubDataCache())
        top_repo_names = [repo.name for repo in top_repos]
        mock_repo_names = [repo.name for repo in MOCK_REPOS]
        self.assertCountEqual(top_repo_names, mock_repo_names)
    
    @patch("utilities.repo_utilities.get_stars_count")
    @patch("utilities.repo_utilities.get_forks_count")
    @patch("utilities.repo_utilities.get_pull_requests_count")
    def test_get_top_repos_by_criteria_with_more_than_n_repos(self, mock_get_pull_requests_count, mock_get_forks_count, mock_get_stars_count):
        self.set_up_mocks(mock_get_stars_count, mock_get_forks_count, mock_get_pull_requests_count)
        
        top_repos_by_stars = get_top_repos_by_criteria(MOCK_REPOS, n=2, criteria=Criteria.STARS, cache=GithubDataCache())
        self.assertEqual([repo.name for repo in top_repos_by_stars], ["ManyStarsRepo", "ManyForksRepo"])

        top_repos_by_forks = get_top_repos_by_criteria(MOCK_REPOS, n=3, criteria=Criteria.FORKS, cache=GithubDataCache())
        self.assertEqual([repo.name for repo in top_repos_by_forks], ["ManyForksRepo", "ManyStarsRepo", "ManyContributionsRepo"])

        top_repos_by_pull_requests = get_top_repos_by_criteria(MOCK_REPOS, n=1, criteria=Criteria.PULL_REQUESTS, cache=GithubDataCache())
        self.assertEqual([repo.name for repo in top_repos_by_pull_requests], ["ManyPullsRepo"])

        top_repos_by_contribution_percentage = get_top_repos_by_criteria(MOCK_REPOS, n=3, criteria=Criteria.CONTRIBUTION_PERCENTAGE, cache=GithubDataCache())
        self.assertEqual([repo.name for repo in top_repos_by_contribution_percentage], ["ManyContributionsRepo", "ManyStarsRepo", "ManyForksRepo"])
        
# mock cache data + get_stars/fork/pull reuquests count results

# todo: consider tests with cache