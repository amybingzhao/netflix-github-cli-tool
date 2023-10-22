import unittest
from github_organization_repo_explorer.models.repo_data import RepoData
from github_organization_repo_explorer.models.criteria import Criteria

class TestRepoData(unittest.TestCase):
    def test_get_stars(self):
        repo_data = RepoData(stars_count=124, forks_count=0, pull_requests_count=32)
        self.assertEqual(repo_data.get_data_for_criteria(Criteria.STARS), 124)

    def test_get_forks(self):
        repo_data = RepoData(stars_count=99, forks_count=12, pull_requests_count=92)
        self.assertEqual(repo_data.get_data_for_criteria(Criteria.FORKS), 12)

    def test_get_pull_requests(self):
        repo_data = RepoData(stars_count=1, forks_count=1, pull_requests_count=0)
        self.assertEqual(repo_data.get_data_for_criteria(Criteria.PULL_REQUESTS), 0)

    def test_get_contribution_percentage_with_zero_denominator(self):
        repo_data = RepoData(stars_count=9999, forks_count=0, pull_requests_count=52)
        self.assertEqual(repo_data.get_data_for_criteria(Criteria.CONTRIBUTION_PERCENTAGE), 0)

    def test_get_contribution_percentage_with_non_zero_denominator(self):
        repo_data = RepoData(stars_count=10222, forks_count=20, pull_requests_count=0)
        self.assertEqual(repo_data.get_data_for_criteria(Criteria.CONTRIBUTION_PERCENTAGE), 0)

        repo_data2 = RepoData(stars_count=7, forks_count=20, pull_requests_count=3)
        self.assertEqual(repo_data2.get_data_for_criteria(Criteria.CONTRIBUTION_PERCENTAGE), 0.15)