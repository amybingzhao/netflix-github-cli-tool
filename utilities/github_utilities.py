from github import Github, Organization, PaginatedList, Repository
from utilities.cache_utilities import GithubDataCache

'''
This file contains all the methods that might need to reach out to the Github API.

We wrap and centralize them for simplified mocking in tests.
'''

def get_organization(github: Github, organization_name: str) -> Organization.Organization:
    try:
        return github.get_organization(organization_name)
    except Exception as e:
        if e.status == 404:
            # maybe pass through e.data?
            print(f"The requested organization {organization_name} does not exist.") # todo: add some actionable info
            exit(1)
        elif e.status == 401:
            print("Unable to authenticate. Please confirm you have access to this organization.")
            exit(1)
        elif e.status == 403:
            print("Is this also forbidden? What's rate limited") # todo revisit these error messages
            exit(1)
        else:
            raise e
        
def get_repos(organization: Organization.Organization, cache: GithubDataCache) -> PaginatedList.PaginatedList[Repository.Repository]:
    cached_repos_or_none = cache.try_get_repos_for_org(organization.name)
    if cached_repos_or_none is not None:
        return cached_repos_or_none
    else:
        repos = organization.get_repos()
        cache.update_repos_for_org(organization.name, repos)
        return repos

def get_stars_count(repo: Repository.Repository) -> int:
    return repo.get_stargazers().totalCount

def get_forks_count(repo: Repository.Repository) -> int:
    repo.get_forks().totalCount

def get_pull_requests_count(repo: Repository.Repository) -> int:
    repo.get_pulls().totalCount,