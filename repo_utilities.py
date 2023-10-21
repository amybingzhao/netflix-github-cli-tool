from github import PaginatedList, Repository
from criteria import Criteria
import heapq

def _get_value_for_criteria(repo: Repository.Repository, criteria: Criteria) -> int | float:
    if criteria == Criteria.STARS.value:
        return repo.get_stargazers().totalCount
    elif criteria == Criteria.FORKS.value:
        return repo.get_forks().totalCount
    elif criteria == Criteria.PULL_REQUESTS.value:
        return repo.get_pulls().totalCount
    elif criteria == Criteria.CONTRIBUTION_PERCENTAGE.value:
        pull_requests_count = repo.get_pulls().totalCount
        forks_count = repo.get_forks().totalCount
        return pull_requests_count / forks_count
    else:
        raise ValueError(f"Unsupported criteria: {criteria}")

def get_top_repos_by_criteria(repos: PaginatedList.PaginatedList[Repository.Repository], n: int, criteria: Criteria) -> list[Repository.Repository]:
    top_repos_with_value = [] # list[tuple[value, repo]]
    for repo in repos:
        value = _get_value_for_criteria(repo, criteria)
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