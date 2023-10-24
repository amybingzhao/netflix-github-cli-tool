from enum import Enum

class Criteria(Enum):
    STARS = "stars"
    FORKS = "forks"
    PULL_REQUESTS = "pull_requests"
    CONTRIBUTION_PERCENTAGE = "contribution_percentage"

def get_string_representation(value: int | float, criteria: Criteria) -> str:
    if criteria == Criteria.STARS:
        return f"{value} stars" if value != 1 else f"{value} star"
    elif criteria == Criteria.FORKS:
        return f"{value} forks" if value != 1 else f"{value} fork"
    elif criteria == Criteria.PULL_REQUESTS:
        return f"{value} pull requests" if value != 1 else f"{value} pull request"
    elif criteria == Criteria.CONTRIBUTION_PERCENTAGE:
        return f"{round(value, 2)}%"