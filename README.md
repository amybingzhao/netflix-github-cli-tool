# netflix-github-cli-tool

## Features to support
For a github organization:
- Top-N repos by # of stars
- Top-N repos by # of forks
- Top-N repos by number of PRs
- Top-N repos by contribution percentage (PRs/forks)

## Testing

### Automated Tests


### Manual Tests
You can test the functionality of this tool against the (Amy-Testing org)[https://github.com/Amy-Testing]

## Decisions
- cache repo data, cache by repo rather than by repo + by category
- is it worth it to cache repos per org? b/c it's just 1 request + want to catch new repos