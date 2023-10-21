#!/usr/bin/env python
import argparse
from github import Github, Repository
from utilities.organization_utilities import get_organization, get_repos
from utilities.repo_utilities import get_top_repos_by_criteria
from models.criteria import Criteria
from utilities.authentication_utilities import get_personal_access_token
from github import Auth
from utilities.cache_utilities import get_github_data_cache

TOP_N_ARG_VALIDATION_ERROR_MESSAGE = "--top-n/-n must be an integer value greater than zero."

def _print_result(top_repos: list[Repository.Repository], organization_name: str, n: int, criteria: Criteria) -> None:
    print(f"Top {n} repos in {organization_name} based on {criteria.value}:")
    for repo in top_repos:
        print(f"\t- {repo.name}")

def _get_authenticated_github_client() -> Github:
    return Github(
        login_or_token=get_personal_access_token(),
        auth=Auth.Token("access_token")
    )

def main(args):
    (organization_name, n, criteria) = (args.organization_name, args.n, Criteria(args.criteria))
    github_client = _get_authenticated_github_client() # todo: authentication, prompt for PAT?
    
    with get_github_data_cache() as cache:
        print(f"Gathering the repos for {organization_name}")
        organization = get_organization(github_client, organization_name)
        repos = get_repos(organization, cache)
        print(f"Found {repos.totalCount} repo(s)")
        
        print(f"Filtering to the top {n} repo(s) based on {criteria.value}")
        top_repos_by_criteria = get_top_repos_by_criteria(repos, n, criteria, cache)
        _print_result(top_repos_by_criteria, args.organization_name, n, criteria)

def validate_top_n_arg(value):
    try:
        value_as_int = int(value)
        if value_as_int < 1:
            raise argparse.ArgumentTypeError(TOP_N_ARG_VALIDATION_ERROR_MESSAGE)
    except:
        raise argparse.ArgumentTypeError(TOP_N_ARG_VALIDATION_ERROR_MESSAGE)
    return value_as_int

def parse_args():
    parser = argparse.ArgumentParser(prog="github_organization_repo_explorer.py", description="For a given Github org, finds the top N repos by the requested criteria.")
    parser.add_argument("organization_name", type=str, help="The name of the org you want to explore")
    parser.add_argument("--top-n", "-n", dest="n", type=validate_top_n_arg, required=False, default=5, help="FILL IN")
    parser.add_argument("--criteria", "-c", dest="criteria", type=str, required=True, choices=[criteria.value for criteria in Criteria], help="FILL IN")
    return parser.parse_args()

if __name__ == "__main__":
    main(parse_args())