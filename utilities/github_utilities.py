from github import Github, Organization, PaginatedList, Repository

from utilities.cache_utilities import GithubDataCache

'''
This file contains all the methods that might need to reach out to the Github API.

We wrap and centralize them for simplified mocking in tests.
'''

ERROR_MESSAGE_BY_ERROR_CODE = {
    401: "ERROR: Bad credentials. Please confirm your access token is entered correctly and that you have access to this organization.",
    403: "ERROR: You've exceeded the Github API rate limits. If you haven't set up a PAT, doing so will increase your allowed requests per hour.",
    404: "ERROR: The requested Github resource does not exist."
}

def get_organization(github: Github, organization_name: str) -> Organization.Organization:
    try:
        return github.get_organization(organization_name)
    except Exception as e:
        if e.status in ERROR_MESSAGE_BY_ERROR_CODE:
            print(ERROR_MESSAGE_BY_ERROR_CODE[e.status])
            exit(1)
        else:
            raise e
        
def get_repos(organization: Organization.Organization, cache: GithubDataCache) -> PaginatedList.PaginatedList[Repository.Repository]:
    cached_repos_or_none = cache.try_get_repos_for_org(organization.name)
    if cached_repos_or_none is not None:
        return cached_repos_or_none
    else:
        try:
            repos = organization.get_repos()
        except Exception as e:
            if e.status in ERROR_MESSAGE_BY_ERROR_CODE:
                print(ERROR_MESSAGE_BY_ERROR_CODE[e.status])
                exit(1)
        cache.update_repos_for_org(organization.name, repos)
        return repos

def get_stars_count(repo: Repository.Repository) -> int:
    try:
        return repo.get_stargazers().totalCount
    except Exception as e:
        if e.status in ERROR_MESSAGE_BY_ERROR_CODE:
            print(ERROR_MESSAGE_BY_ERROR_CODE[e.status])
            exit(1)

def get_forks_count(repo: Repository.Repository) -> int:
    try:
        return repo.get_forks().totalCount
    except Exception as e:
        if e.status in ERROR_MESSAGE_BY_ERROR_CODE:
            print(ERROR_MESSAGE_BY_ERROR_CODE[e.status])
            exit(1)
    

def get_pull_requests_count(repo: Repository.Repository) -> int:
    try:
        return repo.get_pulls().totalCount
    except Exception as e:
        if e.status in ERROR_MESSAGE_BY_ERROR_CODE:
            print(ERROR_MESSAGE_BY_ERROR_CODE[e.status])
            exit(1)