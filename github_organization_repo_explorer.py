#!/usr/bin/env python
import argparse

TOP_N_ARG_VALIDATION_ERROR_MESSAGE = "--top-n/-n must be an integer value greater than zero."

def main(args):
    print(args)
    return

def validate_top_n_arg(value):
    try:
        value_as_int = int(value)
        if value_as_int <= 1:
            raise argparse.ArgumentTypeError(TOP_N_ARG_VALIDATION_ERROR_MESSAGE)
    except:
        raise argparse.ArgumentTypeError(TOP_N_ARG_VALIDATION_ERROR_MESSAGE)
    return value_as_int

def parse_args():
    parser = argparse.ArgumentParser(prog="github_organization_repo_explorer.py", description="For a given Github org, finds the top N repos by the requested criteria.")
    parser.add_argument("org", type=str, help="The name of the org you want to explore")
    parser.add_argument("--top-n", "-n", dest="n", type=validate_top_n_arg, required=False, default=5, help="FILL IN")
    # todo make choices an enum
    parser.add_argument("--criteria", "-c", dest="criteria", type=str, required=True, choices=["stars", "forks", "pull requests", "contribution percentage"], help="FILL IN")
    return parser.parse_args()
    


if __name__ == "__main__":
    main(parse_args())