# netflix-github-cli-tool

## Features
For a github organization, find the:
- Top-N repos by # of stars
- Top-N repos by # of forks
- Top-N repos by number of PRs
- Top-N repos by contribution percentage (PRs/forks)
  - What we're approximating here is how often people who are interested in a repo contribute back to the original repo. By this logic a repo that has e.g. 5 PRs and 0 forks has a higher contribution percentage than a repo with 5 PRs and 1 fork since all people who are interested in it are contributing to the original repo rather than working off of a fork. We achieve this by considering the original repo a fork.
  - In real life we'd probably want to do some user interviews to check that this aligns with how users would interpret contribution percentage

Ties are broken alphabetically by repo name, which should be unique within an org. This is a simple V0 tie breaking method, but if requested we could implement other tiebreakers.

## Installation
- This was written with python 3.10
- To install required dependencies, run `pip install -r requirements.txt` from this directory

## Usage
- There's a convenience bash script that you can run at
  ```
  ./github-organization-repo-explorer <org_name> -n <# of repos to filter to> -c <criteria to filter by>
  ``````
  - It assumes that you have python aliased as `python3.10` though, so if this is not the case you may have to change that
- You can also run this tool by running 
  ```
  python ./github_organization_repo_explorer.py <org_name> -n <# of repos to filter to> -c <criteria to filter by>
  ``
- Help text can be found by running `./github-organization-repo-explorer -h` or `python ./github_organization_repo_explorer.py -h`

## How it works

While building this, I assumed that this is a CLI tool that might be used by individual users for exploration rather than e.g. a tool that is used by some cron job to periodically scrape data about github orgs.

When you run this CLI tool it will:
1. Prompt you for a PAT if you haven't registered one with it before
    - You can choose to skip this and use the tool as an unauthenticated user
    - If you add one, it'll be stored in a git-ignored .env file (arbitrarily stored adjacent to the file that handles the business logic for this for now)
2. Load cached results if any exist from a local git-ignored .pkl file
3. Query the Github REST API for repos corresponding to the org you passed in
    - This query may use cached if this org has been queried in the last 60 min
4. For each of those repos, it will look up the stars, forks, and pull requests
    - These queries may also be cached per-repo if the repo has been queried in the last 60 min
    - Right now we fetch and cache the stars, forks, and PR data for a repo in an all-or-nothing fashion b/c we assume that if the user is asking about e.g. stars they might follow-up with a quetsion about e.g. forks, but if this turns out not to be the case + we're hitting performance issues because of the extra requests to fetch data about other criteria, we could also fetch and cache the stars, forks, and PR data more granularly.
5. As data is gathered for each repo in step 4, maintain a heap of size N that has the top N repos based on the selected criteria. Whenever we encounter a repo that has a greater value for the selected criteria than the min value in this heap, pop the min value off and push the new repo onto the heap.
    - This assumes that the number of repos (r) is usually much larger than n. With this approach, the runtime of this step is O(rlogn).
    - Alternatively, we could just sort the list of repos and pick the top n -- this would take O(rlogr) time.
    - We should validate whether it's true that r >> n through metrics/logging
6. Print the results of 5 to the console
7. Save any new cached results to a .pkl file

### Interesting decisions

#### Using pygithub

There are [many python libraries](https://docs.github.com/en/rest/overview/libraries?apiVersion=2022-11-28#python) that wrap the Github REST API. `pygithub` seemed to be the one with by far the most stars/forks, which suggests it's the most battle-tested, and it seems to be still actively maintained (last update was 2 weeks ago).

#### Prompting for a PAT rather than just using an unauthenticated user

An interesting challenge with writing this tool was wrestling with the limitations of the Github API. For gathering data about repos, Github exposes fine-grained API endpoints (i.e. there are different endpoints for stargazers, PRs, and forks), which means we're making multiple queries per repo. This may not be an issue when working with orgs that have a small number of repos, but many orgs that have popular open-source repos like Facebook and Netflix have 100-300 repos. If we're making 3 requests for each of 300 repos, that's already 900 requests, and if we add on more pieces of data we care about this can increase quickly.

(Note: while Github technically allows an unlimited # of repos, it seems like in practice orgs tend to have at most 100s of repos so we don't worry too much about handling orgs with 1000s of repos ore more just yet.)

An unauthenticated user can only make [60 requests per hour](https://docs.github.com/en/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28#rate-limits-for-requests-from-personal-accounts). From the math above, we can see that this can be quickly exhausted, which means it's a necessity to allow the user to authenticate in some way.

A user authenticated with a user access token can make 5k requests per hour, which is a much more reasonable limit to work with for this tool (although it's still possible there are other tools also making requests with this same access token). 

For now we store the PAT locally in a .env file, but if this were a tool distributed to engs in an org there'd probably be some best practice way to store and retrieve secrets like this.

#### Caching Github data

Right now we cache the repos for each org as well as the stars, forks, and PR count data for each repo between invocations of this tool in a local .pkl file.

Some assumptions baked into this are:
- If a user queries an org, they are likely to query that org again to learn more about it (e.g. if they first ask for the top 5 repos by stars, they may then have follow-ups about what the top 10 are or what the top 5 by forks are)
- A user is probably performing these repeated queries in a relatively short amount of time (e.g. across 5-30 min), and it's unlikely that the Github data changes in a way that noticeably impacts the results during that time.
     - We're assuming they'd prefer responsiveness over guaranteed freshness
     - We do provide a `--refresh-cache` flag if the user does want to get fresh data though
- Orgs that a user cares about are probably specific to that user, and so it makes sense to just store cache data locally. If there are common orgs that many users care about we could consider deploying a caching service like Redis so users can share data and benefit from each others' queries.

The caching helps with staying under the rate limits as well as performance. Each request to Github seems to take ~100s of ms, and this can really add up if you're issuing 100s requests.

We also use an internal CACHE_VERSION in the `GithubDataCache` class as a mechanism for clearing caches when the data we care about changes (e.g. if we need to start requesting a new piece of data, we can't use the cached results b/c they won't have the piece of data we care about).

The 60 min TTL is a best initial guess based on how long we think a working session might be + how much staleness can be tolerated, but it can be tuned based on user feedback.

#### Output format

We output the results as a list in descending order based on the value for the requested criteria. We also output the value of the criteria next to the repo name so the end user can understand the ordering.

When we're fetching data for repos, we print out a message since this step can take a long time if there are many repos. This gives  the user gets some indicator that the program is progressing and not just hanging.


### Enhancements to consider

- Metrics and logging
  - To figure out how we should evolve this tool after its release, we'll want to understand things like how often it's being used, what the most popularly queried orgs are, what the commonly used args are in case we need to update the defaults, commonly encountered errors, and how long different stages are taking to see if we need to make performance improvements
  - These pieces of info should be captured per invocation and sent to some centralized logging/monitoring service like Splunk
- More robust error handling
  - I handled the errors that I thought were likely to be encountered but if I had more time to spend on this I'd try to stress test interactions with the Github API to make sure we've handled all the rough edges (e.g. Github server is down, access token is expired, fine-grained access token is provided rather than classic PAT)
- Figure out packaging and installation
  - I'm not super familiar with how python tools tend to be packaged and distributed. At Asana we have a monorepo so engs just git pull to get new tools/updates to existing tools. I assume Netflix has some best practice or if not we could lean on industry best practices.
- Batch/parallelize requests to speed up fetching info about repos
  - Right now we query repo data in series. This can be pretty slow if we're querying over a large # of repos (on the order of minutes)
  - These requests are highly parallelizable though so we could issue them in parallel to speed up the wall time spent waiting. We could issue them in batches of a fixed size to be polite and avoid overloading the Github server.
  - We could monitor the metrics around how long this step is taking to decide if we want to add this functionality
- Support fine-grained personal access tokens/Github Apps/other authentication formats
  - Based on requests/organizational needs, we could update how authentication is handled
- Consider special handling around non-public repos
  - e.g. indicating in the output if a repo is non-public so the end user can make more informed decisions about sharing the results, or allowing the user to filter to only public repos
- Pretty printing errors/infos/warns and offering different verbosity levels
  - This would make the output more readable by the end user
- Linting
  - Setting up a linter would help with the readability of this project


## Testing

### Automated Tests
Run `python -m unittest` from this directory. (It should run 23 tests.)

The tests cover the business logic around:
- `tests/models/test_repo_data.py`
  - Calculating # of stars, # of forks, # of PRs, and contribution percentage per repo
- `tests/utilities/test_authentication_utilities.py`
  - Getting and setting the PAT
  - Choosing to not set a PAT
- `tests/utilities/test_cache_utilities.py`
  - Updating data in the cache
  - Retrieving unexpired data in the cache
  - Trying to retrieve data from the cache but it's stale
  - Writing and loading the cache data to a .pkl file
  - Ignoring saved cache data if `refresh=True`
- `tests/utilities/repo_utilities.py`
  - Getting the top N repos if there are no repos in the org
  - Getting the top N repos filtered by each available criteria when there are more than N repos in the org
  - Getting the top N repos when there are more than 0 but fewer than N repos in the org

Notably we don't test the methods in `utilities/github_utilites.py` because they are mostly wrappers around talking to the github API via `pygithub`, which we assume has its own tests. We also mock these out in all of our tests rather than reaching out to the actual Github API so that they can run as unit tests that are quick and robust to the Github API being inaccessible.

### Manual Tests
You can test the functionality of this tool against the (Amy-Testing org)[https://github.com/Amy-Testing].

Repos in this org:
- MostForks - 0 stars, 3 forks, 0 PRs
- MostStars - 1 star, 0 forks, 1 PR
- MostPullRequests - 0 stars, 1 forks, 3 PRs
- HighestContributionPercentage - 0 stars, 0 forks, 2 PRs
- ForkOfMostForks - 0 stars, 0 forks, 0 PRs
- AnotherForkOfMostForks - 0 stars, 0 forks, 0 PRs

Ranking by # of stars:
1. MostStars (1)
2. AnotherForkOfMostForks (0, first alphabetically amongst the rest)
3. ForkOfMostForks (0)
4. HighestContributionPercentage (0)
5. MostForks (0)
6. MostPullRequests (0)

Ranking by # of forks:
1. MostForks (3)
2. MostPullRequests (1)
3. AnotherForkOfMostForks (0)
4. ForkOfMostForks (0)
5. HighestContributionPercentage (0)
6. MostStars (0)

Ranking by # of PRs:
1. MostPullRequests (3)
2. HighestContributionPercentage (2)
3. MostStars (1)
4. AnotherForkOfMostForks (0)
5. ForkOfMostForks (0)
6. MostForks (0)

Ranking by contribution percentage:
1. HighestContributionPercentage (2 PRs, 0 fork --> (2/(0 forks + 1 original repo)) = 200%)
2. MostPullRequests (3 PRs, 1 fork --> (3/(1 forks + 1 original repo)) = 150%)
3. MostStars (1 PR, 0 forks --> (1/(0 forks + 1 original repo)) = 100%)
4. AnotherForkOfMostForks (0 PRs, 0 forks --> 0%)
5. ForkOfMostForks (0 PRs, 0 forks --> 0%)
6. MostForks (0 PRs, 3 forks --> 0%)

Other manual test cases:
- Running w/ and w/o a PAT set up
  - w/o a PAT you get prompted to set one up
  - w/o a PAT you get rate limited if you try to query an org like facebook with many repos without any cached data
- w/ and w/o cached data
- updating the cache version refetches data