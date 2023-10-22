from github_organization_repo_explorer.models.criteria import Criteria

class RepoData:
    def __init__(self, stars_count: int, forks_count: int, pull_requests_count: int):
        self.stars_count = stars_count
        self.forks_count = forks_count
        self.pull_requests_count = pull_requests_count
    
    def get_data_for_criteria(self, criteria: Criteria) -> int | float:
        if criteria == Criteria.STARS:
            return self.stars_count
        elif criteria == Criteria.FORKS:
            return self.forks_count
        elif criteria == Criteria.PULL_REQUESTS:
            return self.pull_requests_count
        elif criteria == Criteria.CONTRIBUTION_PERCENTAGE:
            return self.pull_requests_count / self.forks_count
        else:
            raise ValueError(f"Unknown criteria: {criteria.value}")
