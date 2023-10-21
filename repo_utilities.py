from github import PaginatedList, Repository
from criteria import Criteria
import heapq
from cache_utilities import GithubDataCache
from typing import Callable
from models.repo_data import RepoData

def _get_value_for_basic_criteria(repo: Repository.Repository, criteria: Criteria, cache: GithubDataCache, fetch_method: Callable[[Repository.Repository], int]) -> int | float:
    cached_value = cache.try_get_data_for_repo(repo.name, criteria)
    if cached_value is not None:
        return cached_value
    else:
        updated_value = fetch_method(repo)
        cache.update_data_for_repo(repo.name, criteria, updated_value)
        return updated_value

def _get_value_for_criteria(repo: Repository.Repository, criteria: Criteria, cache: GithubDataCache) -> int | float:
    repo_data = cache.try_get_data_for_repo(repo.name)
    
    if repo_data is None:
        repo_data = RepoData(
            stars_count = repo.get_stargazers().totalCount,
            forks_count = repo.get_forks().totalCount,
            pull_requests_count = repo.get_pulls().totalCount,
        )
        cache.update_data_for_repo(repo.name, repo_data)
    
    return repo_data.get_data_for_criteria(criteria)

def get_top_repos_by_criteria(repos: PaginatedList.PaginatedList[Repository.Repository], n: int, criteria: Criteria, cache: GithubDataCache) -> list[Repository.Repository]:
    top_repos_with_value = [] # list[tuple[value, repo]]
    for repo in repos:
        value = _get_value_for_criteria(repo, criteria, cache)
        if len(top_repos_with_value) < n:
            # if we have fewer than n items in our top_repos list, add this repo in
            top_repos_with_value.append((value, repo))
            heapq.heapify(top_repos_with_value)
        else:
            # if we have more than n items, we check if this repo has a higher value than the 
            # smallest (value, repo) pair currently in our top_repos heap. if it does, then 
            # remove the smallest value and push the new one onto our heap
            if value > top_repos_with_value[0][0]:
                heapq.heapreplace(top_repos_with_value, (value, repo))

    return [repo_with_value[1] for repo_with_value in top_repos_with_value]