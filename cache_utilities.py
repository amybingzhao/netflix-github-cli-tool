from contextlib import contextmanager
import os
import pickle
from github import PaginatedList, Repository
import time
from criteria import Criteria
from models.repo_data import RepoData

CACHE_DIRECTORY = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_FILE = os.path.join(CACHE_DIRECTORY, "github_data.pkl")
CACHE_VERSION = "1.0.0"

class GithubDataCache:
    TIME_TO_LIVE_SECONDS = 60 * 60

    def __init__(self):
        self.repos_by_organization_name = {}
        self.last_checked_time_by_organization_name = {}
        self.repo_data_by_repo_name = {}
        self.last_checked_time_by_repo_name = {}
        self.version = CACHE_VERSION
    
    def _is_stale(self, current_time: int, last_checked_time: int) -> bool:
        return current_time - last_checked_time > self.TIME_TO_LIVE_SECONDS

    def update_repos_for_org(self, organization_name: str, repos: PaginatedList.PaginatedList[Repository.Repository]) -> None:
        self.repos_by_organization_name[organization_name] = repos
        self.last_checked_time_by_organization_name[organization_name] = time.time()
    
    def try_get_repos_for_org(self, organization_name: str) -> PaginatedList.PaginatedList[Repository.Repository] | None:
        current_time = time.time()
        
        repos = None
        if organization_name in self.repos_by_organization_name:
            if self._is_stale(current_time, self.last_checked_time_by_organization_name[organization_name]):
                del self.repos_by_organization_name[organization_name]
                del self.last_checked_time_by_organization_name[organization_name]
            else:
                repos = self.repos_by_organization_name[organization_name]
        
        return repos
    
    def update_data_for_repo(self, repo_name: str, repo_data: RepoData) -> None:
        current_time = time.time()
        self.repo_data_by_repo_name[repo_name] = repo_data
        self.last_checked_time_by_repo_name[repo_name] = current_time

    def try_get_data_for_repo(self, repo_name: str) -> int | None:
        current_time = time.time()
        
        data = None
        if repo_name in self.repo_data_by_repo_name:
            if self._is_stale(current_time, self.last_checked_time_by_repo_name[repo_name]):
                del self.repo_data_by_repo_name[repo_name]
                del self.last_checked_time_by_repo_name[repo_name]
            else:
                data = self.repo_data_by_repo_name[repo_name]
        
        return data
    
def _try_load_github_data_cache():
    if not os.path.exists(CACHE_DIRECTORY):
        return GithubDataCache()
    else:
        try:
            with open(CACHE_FILE, "rb") as f:
                cache = pickle.load(f)
                return cache if cache.version == CACHE_VERSION else GithubDataCache()
        except Exception:
            # if we run into an unexpected error loading the cache (e.g because the pickle file is corrupted),
            # just return and empty cache
            return GithubDataCache()

@contextmanager
def get_github_data_cache():
    cache = _try_load_github_data_cache()
    try:
        yield cache
    finally:
        os.makedirs(CACHE_DIRECTORY, exist_ok=True)
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(cache, f)
