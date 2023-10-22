# netflix-github-cli-tool

## Features
For a github organization, find the:
- Top-N repos by # of stars
- Top-N repos by # of forks
- Top-N repos by number of PRs
- Top-N repos by contribution percentage (PRs/forks)

## Installation
- This was written with python 3.10
- To install required dependencies, run `pip install -r requirements.txt`

## Usage
- There's a convenience bash script that you can run at `./github-organization-repo-explorer <args>`
  - It assumes that you have python aliased as `python3.10` though, so if this is not the case you may have to change that

## Testing

### Automated Tests
Run `python -m unittest` from the git root

### Manual Tests
You can test the functionality of this tool against the (Amy-Testing org)[https://github.com/Amy-Testing].

Repos in this org:
- MostForks - 0 stars, 3 forks, 0 PRs
- MostStars - 1 star, 0 forks, 1 PR
- MostPullRequests - 0 stars, 0 forks, 3 PRs
- HighestContributionPercentage - 0 stars, 1 forks, 2 PRs (check if we need to add more PRs here to compete with MostPullRequests depending on what 0 forks implies for contribution percentage)
- ForkOfMostForks - 0 stars, 0 forks, 0 PRs
- AnotherForkOfMostForks - 0 stars, 0 forks, 0 PRs

Other manual test cases:
- Running w/ and w/o a PAT set up --> w/o a PAT you get rate limited if you try to query an org like facebook with many repos without any cached data
- w/ and w/o cached data
- updating the cache version

## Decisions
- cache repo data, cache by repo rather than by repo + by category
- is it worth it to cache repos per org? b/c it's just 1 request + want to catch new repos
- assume responsiveness is more important than freshness

## To-do
- Stress test interactions with Github so we can handle network errors/bad responses better
- More unit tests
- Linting
- Figure out packaging and installation
- Batch requests to speed up fetching info about repos
- Support fine-grained personal access tokens
- Consider private repos
- Pretty printing errors/infos/warns
- Log how long different stages take