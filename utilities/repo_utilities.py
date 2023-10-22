import heapq
from github import PaginatedList, Repository

from models.criteria import Criteria
from models.repo_data import RepoData
from utilities.cache_utilities import GithubDataCache
from utilities.github_utilities import get_stars_count, get_forks_count, get_pull_requests_count

def _get_value_for_criteria(repo: Repository.Repository, criteria: Criteria, cache: GithubDataCache) -> int | float:
    repo_data = cache.try_get_data_for_repo(repo)
    
    if repo_data is None:
        repo_data = RepoData(
            stars_count = get_stars_count(repo),
            forks_count = get_forks_count(repo),
            pull_requests_count = get_pull_requests_count(repo),
        )
        cache.update_data_for_repo(repo, repo_data)
    
    return repo_data.get_data_for_criteria(criteria)

def get_top_repos_by_criteria(repos: PaginatedList.PaginatedList[Repository.Repository], n: int, criteria: Criteria, cache: GithubDataCache) -> list[Repository.Repository]:
    top_repos_with_value = [] # list[tuple[value, repo]]
    for repo in repos:
        value = _get_value_for_criteria(repo, criteria, cache)
        if len(top_repos_with_value) < n:
            # if we have fewer than n items in our top_repos list, add this repo in
            heapq.heappush(top_repos_with_value, (value, repo.name, repo))
        else:
            # if we have more than n items, we check if this repo has a higher value than the 
            # smallest (value, repo) pair currently in our top_repos heap. if it does, then 
            # remove the smallest value and push the new one onto our heap
            (min_value, min_value_repo_name, _) = top_repos_with_value[0]
            if value > min_value or value == min_value and repo.name > min_value_repo_name:
                heapq.heapreplace(top_repos_with_value, (value, repo.name, repo))
    return [repo_with_value[2] for repo_with_value in heapq.nlargest(n, top_repos_with_value)]