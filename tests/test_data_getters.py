from github_analyser.issues import get_issues
from github_analyser.repos import get_repos


def test_get_repos(mock_github):  # noqa: ARG001
    repos = get_repos("alan-turing-institute")
    assert len(repos) == 10
    assert set(repos.columns) == {
        "id",
        "name",
        "url",
        "updated_at",
        "languages",
        "is_private",
        "is_archived",
    }
    assert "github-analyser" in repos.loc[:, "name"].values
    assert (
        "https://github.com/alan-turing-institute/github-analyser"
        in repos.loc[:, "url"].values
    )


def test_get_issues(mock_github):  # noqa: ARG001
    issues = get_issues("alan-turing-institute", "github-analyser")
    assert len(issues) == 3
    assert set(issues.columns) == {
        "title",
        "body",
        "author",
        "created_at",
        "closed_at",
        "comments",
        "labels",
    }
    assert "Markus needs new socks" in issues.loc[:, "title"].values
    assert "Kinda urgent" in issues.loc[:, "body"].values
    assert "mhauru" in issues.loc[:, "author"].values
    assert "2024-02-29T12:11:12Z" in issues.loc[:, "created_at"].values
    assert "2024-02-23T16:49:59Z" in issues.loc[:, "closed_at"].values
    assert ["mhauru", "rwood-97"] == issues.loc[2, "comments"]
    assert ["help needed", "anatomy"] == issues.loc[2, "labels"]
