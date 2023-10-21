from contextlib import contextmanager
import os
import pickle
from github import PaginatedList, Repository
import time
from criteria import Criteria

CACHE_DIRECTORY = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_FILE = os.path.join(CACHE_DIRECTORY, "github_data.pkl")

class GithubDataCache:
    TIME_TO_LIVE_SECONDS = 60 * 60

    def __init__(self):
        self.repos_by_organization_name = {}
        self.last_checked_time_by_organization_name = {}
        self.value_by_criteria_by_repo_name = {}
        self.last_checked_time_by_criteria_by_repo_name = {}
    
    def update_repos_for_org(self, organization_name: str, repos: PaginatedList.PaginatedList[Repository.Repository]) -> None:
        self.repos_by_organization_name[organization_name] = repos
        self.last_checked_time_by_organization_name[organization_name] = time.time()
    
    def _is_stale(self, current_time: int, last_checked_time: int) -> bool:
        return current_time - last_checked_time > self.TIME_TO_LIVE_SECONDS

    def try_get_repos_for_org(self, organization_name: str) -> PaginatedList.PaginatedList[Repository.Repository] | None:
        current_time = time.time()
        if organization_name in self.repos_by_organization_name:
            if self._is_stale(current_time, self.last_checked_time_by_organization_name[organization_name]):
                del self.repos_by_organization_name[organization_name]
                del self.last_checked_time_by_organization_name[organization_name]
                return None
            else:
                return self.repos_by_organization_name[organization_name]
        return None
    
    def update_data_for_repo(self, repo_name: str, criteria: Criteria, value: int) -> None:
        current_time = time.time()
        criteria_key = criteria.value
        if repo_name in self.value_by_criteria_by_repo_name:
            self.value_by_criteria_by_repo_name[repo_name][criteria_key] = value
            self.last_checked_time_by_criteria_by_repo_name[repo_name][criteria_key] = current_time
        else:
            self.value_by_criteria_by_repo_name[repo_name] = { criteria_key: value}
            self.last_checked_time_by_criteria_by_repo_name[repo_name] = { criteria_key: current_time}

    def try_get_data_for_repo(self, repo_name: str, criteria: Criteria) -> int | None:
        current_time = time.time()
        criteria_key = criteria.value
        if repo_name in self.value_by_criteria_by_repo_name and criteria_key in self.value_by_criteria_by_repo_name[repo_name]:
            if self._is_stale(current_time, self.last_checked_time_by_criteria_by_repo_name[repo_name][criteria_key]):
                del self.value_by_criteria_by_repo_name[repo_name][criteria_key]
                del self.last_checked_time_by_criteria_by_repo_name[repo_name][criteria_key]
            else:
                return self.value_by_criteria_by_repo_name[repo_name][criteria_key]
        else:
            return None
    
def _try_load_github_data_cache():
    if not os.path.exists(CACHE_DIRECTORY):
        return GithubDataCache()
    else:
        try:
            with open(CACHE_FILE, "rb") as f:
                return pickle.load(f)
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
