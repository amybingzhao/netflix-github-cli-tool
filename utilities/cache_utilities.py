from contextlib import contextmanager
import os
import pickle
import time

from github import PaginatedList, Repository

from models.repo_data import RepoData

CACHE_DIRECTORY = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_FILE = os.path.join(CACHE_DIRECTORY, "github_data.pkl")
CACHE_VERSION = 1
TIME_TO_LIVE_SECONDS = 60 * 60

class GithubDataCache:
    def __init__(self):
        self.repos_by_organization_name = {}
        self.last_checked_time_by_organization_name = {}
        self.repo_data_by_repo_full_name = {}
        self.last_checked_time_by_repo_full_name  = {}
        self.version = CACHE_VERSION
    
    def _is_stale(self, current_time: int, last_checked_time: int) -> bool:
        return current_time - last_checked_time > TIME_TO_LIVE_SECONDS
    
    # we use the repo full name in case there are collisions across orgs
    def _get_repo_key(self, repo: Repository.Repository) -> str:
        return repo.full_name
    
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
    
    def update_data_for_repo(self, repo: Repository.Repository, repo_data: RepoData) -> None:
        current_time = time.time()
        repo_key = self._get_repo_key(repo)
        self.repo_data_by_repo_full_name[repo_key] = repo_data
        self.last_checked_time_by_repo_full_name[repo_key] = current_time

    def try_get_data_for_repo(self, repo: Repository.Repository) -> int | None:
        current_time = time.time()
        repo_key = self._get_repo_key(repo)

        data = None
        if repo_key in self.repo_data_by_repo_full_name:
            if self._is_stale(current_time, self.last_checked_time_by_repo_full_name[repo_key]):
                del self.repo_data_by_repo_full_name[repo_key]
                del self.last_checked_time_by_repo_full_name[repo_key]
            else:
                data = self.repo_data_by_repo_full_name[repo_key]
        
        return data
    
def _try_load_github_data_cache(refresh: bool) -> GithubDataCache:
    if not os.path.exists(CACHE_FILE) or refresh:
        return GithubDataCache()
    else:
        try:
            with open(CACHE_FILE, "rb") as f:
                cache = pickle.load(f)
                if cache.version == CACHE_VERSION:
                    print("Note: Found cached data that will be used if not stale. If you want to re-fetch all data, re-run this command with `--refresh-cache`.\n")
                    return cache
                else:
                    return GithubDataCache()
        except Exception:
            # if we run into an unexpected error loading the cache (e.g because the pickle file is corrupted),
            # just return and empty cache
            return GithubDataCache()

@contextmanager
def get_github_data_cache(refresh=False):
    cache = _try_load_github_data_cache(refresh)
    try:
        yield cache
    except Exception as e:
        raise e
    else:
        os.makedirs(CACHE_DIRECTORY, exist_ok=True)
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(cache, f)
