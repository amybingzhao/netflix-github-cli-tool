#!/usr/bin/env python
import argparse
from github import Github, Repository
from organization_utilities import get_organization, get_repos
from repo_utilities import get_top_repos_by_criteria
from criteria import Criteria

TOP_N_ARG_VALIDATION_ERROR_MESSAGE = "--top-n/-n must be an integer value greater than zero."

def print_result(top_repos: list[Repository.Repository], organization_name: str, n: int, criteria: str) -> None:
    print(f"Top {n} repos in {organization_name} based on {criteria}:")
    for repo in top_repos:
        print(f"\t- {repo.name}")

def main(args):
    github = Github() # todo: authentication, prompt for PAT?
    organization = get_organization(github, args.organization_name)
    repos = get_repos(organization)
    top_repos_by_criteria = get_top_repos_by_criteria(repos, args.n, args.criteria)
    print_result(top_repos_by_criteria, args.organization_name, args.n, args.criteria)

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