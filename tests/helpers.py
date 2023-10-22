from unittest.mock import MagicMock
from github_organization_repo_explorer.models.repo_data import RepoData
from github_organization_repo_explorer.models.criteria import Criteria

def create_mock_repository(organization_name: str, repo_name: str):
    mock_repository = MagicMock()
    mock_repository.name = repo_name
    mock_repository.full_name = f"{organization_name}/{repo_name}"
    return mock_repository
    
def assertRepoDataIsEqual(repo_data1: RepoData, repo_data2: RepoData) -> None:
    assert repo_data1.get_data_for_criteria(Criteria.STARS) == repo_data2.get_data_for_criteria(Criteria.STARS)
    assert repo_data1.get_data_for_criteria(Criteria.FORKS) == repo_data2.get_data_for_criteria(Criteria.FORKS)
    assert repo_data1.get_data_for_criteria(Criteria.PULL_REQUESTS) == repo_data2.get_data_for_criteria(Criteria.PULL_REQUESTS)
    assert repo_data1.get_data_for_criteria(Criteria.CONTRIBUTION_PERCENTAGE) == repo_data2.get_data_for_criteria(Criteria.CONTRIBUTION_PERCENTAGE)