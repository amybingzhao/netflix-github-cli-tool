from enum import Enum

class Criteria(Enum):
    STARS = "stars"
    FORKS = "forks"
    PULL_REQUESTS = "pull_requests"
    CONTRIBUTION_PERCENTAGE = "contribution_percentage"