import unittest
from unittest.mock import patch, mock_open
import pickle 

from github_organization_repo_explorer.utilities.cache_utilities import GithubDataCache, get_github_data_cache, CACHE_DIRECTORY, CACHE_FILE
from github_organization_repo_explorer.models.repo_data import RepoData
from tests.helpers import create_mock_repository, assertRepoDataIsEqual

class TestGithubDataCache(unittest.TestCase):
    def test_get_repos_for_org_with_no_data(self):
        cache = GithubDataCache()
        self.assertEqual(cache.try_get_repos_for_org("random-org"), None)
    
    def test_update_repos_for_org(self):
        cache = GithubDataCache()
        organization_name = "cool-org"
        repos = [create_mock_repository(organization_name, "RepoA"), create_mock_repository(organization_name, "AnotherRepo1")]
        
        cache.update_repos_for_org(organization_name, repos)
        self.assertCountEqual(cache.try_get_repos_for_org(organization_name), repos)
    
    @patch("time.time")
    def test_get_repos_for_org_with_fresh_data(self, time_mock):
        time_mock.return_value = 1697943670.604693
        cache = GithubDataCache()
        organization_name = "hello"
        repos = [create_mock_repository(organization_name, "there")]

        cache.update_repos_for_org(organization_name, repos)
        time_mock.return_value = 1697943670.604693 + 500
        self.assertCountEqual(cache.try_get_repos_for_org(organization_name), repos)
    
    @patch("time.time")
    def test_get_repos_for_org_with_stale_data(self, time_mock):
        time_mock.return_value = 1234.3210
        cache = GithubDataCache()
        organization_name = "cool-cats"
        repos = [create_mock_repository(organization_name, "123")]

        cache.update_repos_for_org(organization_name, repos)
        self.assertCountEqual(cache.try_get_repos_for_org(organization_name), repos)

        time_mock.return_value = 1234.3210 + 3700 # todo don't ahrdcode this
        self.assertEqual(cache.try_get_repos_for_org(organization_name), None)

    def test_get_data_for_repo_with_no_data(self):
        cache = GithubDataCache()
        mock_repo = create_mock_repository("org", "repo-name")
        self.assertEqual(cache.try_get_data_for_repo(mock_repo), None)
    
    def test_update_data_for_repo(self):
        cache = GithubDataCache()
        mock_repo = create_mock_repository("org", "repo-name2")
        
        initial_repo_data = RepoData(stars_count=1, forks_count=2, pull_requests_count=3)
        cache.update_data_for_repo(mock_repo, initial_repo_data)
        assertRepoDataIsEqual(cache.try_get_data_for_repo(mock_repo), initial_repo_data)
        
        updated_repo_data = RepoData(stars_count=12, forks_count=0, pull_requests_count=34)
        cache.update_data_for_repo(mock_repo, updated_repo_data)
        assertRepoDataIsEqual(cache.try_get_data_for_repo(mock_repo), updated_repo_data)
    
    @patch("time.time")
    def test_get_data_for_repo_with_fresh_data(self, time_mock):
        cache = GithubDataCache()
        mock_repo = create_mock_repository("org", "repo-name2")
        
        starting_time = 999.88
        time_mock.return_value = starting_time
        repo_data = RepoData(stars_count=0, forks_count=0, pull_requests_count=13)
        cache.update_data_for_repo(mock_repo, repo_data)

        time_mock.return_value = starting_time + 30
        assertRepoDataIsEqual(cache.try_get_data_for_repo(mock_repo), repo_data)
    
    @patch("time.time")
    def test_get_data_for_repo_with_stale_data(self, time_mock):
        cache = GithubDataCache()
        mock_repo = create_mock_repository("org", "repo-name2")
        
        starting_time = 1697944486.3507898
        time_mock.return_value = starting_time
        repo_data = RepoData(stars_count=0, forks_count=0, pull_requests_count=13)
        cache.update_data_for_repo(mock_repo, repo_data)

        time_mock.return_value = starting_time + 5000
        self.assertEqual(cache.try_get_data_for_repo(mock_repo), None)
    
    @patch("os.path.exists")
    def test_get_github_data_cache_loads_existing_data(self, mock_exists):
        mock_exists.return_value = True
        cache = GithubDataCache()
        mock_repo = create_mock_repository("org", "repo-name2")
        repo_data = RepoData(stars_count=0, forks_count=0, pull_requests_count=13)
        cache.update_data_for_repo(mock_repo, repo_data)
        pickled_cache = pickle.dumps(cache)

        with patch("builtins.open", mock_open(read_data=pickled_cache)):
            with get_github_data_cache(refresh=False) as loaded_cache:
                assertRepoDataIsEqual(loaded_cache.try_get_data_for_repo(mock_repo), repo_data)
    
    @patch("os.path.exists")
    def test_get_github_data_cache_creates_new_cache_if_no_cached_data(self, mock_exists):
        mock_exists.return_value = False
        cache = GithubDataCache()
        mock_repo = create_mock_repository("org", "repo-name2")
        repo_data = RepoData(stars_count=0, forks_count=0, pull_requests_count=13)
        cache.update_data_for_repo(mock_repo, repo_data)
        with get_github_data_cache(refresh=False) as loaded_cache:
            self.assertEqual(loaded_cache.try_get_data_for_repo(mock_repo), None)
    
    @patch("os.path.exists")
    def test_git_github_data_cache_creates_new_cache_if_refresh(self, mock_exists):
        mock_exists.return_value = True
        cache = GithubDataCache()
        mock_repo = create_mock_repository("org", "repo-name2")
        repo_data = RepoData(stars_count=0, forks_count=0, pull_requests_count=13)
        cache.update_data_for_repo(mock_repo, repo_data)
        pickled_cache = pickle.dumps(cache)

        with patch("builtins.open", mock_open(read_data=pickled_cache)):
            with get_github_data_cache(refresh=True) as loaded_cache:
                self.assertEqual(loaded_cache.try_get_data_for_repo(mock_repo), None) 
    
    # _pickle.PicklingError: Can't pickle <class 'unittest.mock.MagicMock'>: it's not the same object as unittest.mock.MagicMock
    # @patch("os.path.exists")
    # @patch("github_organization_repo_explorer.utilities.cache_utilities.CACHE_VERSION")
    # def test_get_github_data_cache_creates_new_cache_if_cache_version_has_changed(self, mock_cache_version, mock_exists):
    #     mock_exists.return_value = True
    #     mock_cache_version.return_value = 12

    #     cache = GithubDataCache()
    #     mock_repo = create_mock_repository("org", "repo-name2")
    #     repo_data = RepoData(stars_count=0, forks_count=0, pull_requests_count=13)
    #     cache.update_data_for_repo(mock_repo, repo_data)
    #     pickled_cache = pickle.dumps(cache)

    #     mock_cache_version.return_value = 13
    #     with patch("builtins.open", mock_open(read_data=pickled_cache)):
    #         with get_github_data_cache(refresh=False) as loaded_cache:
    #             self.assertEqual(loaded_cache.try_get_data_for_repo(mock_repo), None) 
    
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("pickle.dump")
    def test_get_github_data_cache_stores_cache_data(self, mock_dump, mock_makedirs, mock_exists):
        mock_exists.return_value = False

        with patch("builtins.open", mock_open()):
            with get_github_data_cache(refresh=True) as cache:
                mock_repo = create_mock_repository("org", "repo-name2")
                repo_data = RepoData(stars_count=0, forks_count=0, pull_requests_count=13)
                cache.update_data_for_repo(mock_repo, repo_data)
        mock_makedirs.assert_called_once_with(CACHE_DIRECTORY, exist_ok=True)
        mock_dump.assert_called_once() # todo: try to make this more specific

# todo: consider tests with more than one org/one repo in the cache