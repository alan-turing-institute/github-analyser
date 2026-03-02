from github_analyser.commits import get_commits
from github_analyser.issues import get_issues
from github_analyser.pull_requests import get_pull_requests
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
        "is_fork",
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


def test_get_commits_empty_repo(mock_github):  # noqa: ARG001
    commits = get_commits("alan-turing-institute", "empty-repo")
    assert len(commits) == 0
    assert set(commits.columns) == {
        "id",
        "hash",
        "message",
        "author",
        "date",
        "changed_files",
        "additions",
        "deletions",
        "pr_id",
        "repo_id",
    }


def test_get_pull_requests_empty_repo(mock_github):  # noqa: ARG001
    prs = get_pull_requests("alan-turing-institute", "empty-repo")
    assert len(prs) == 0
    assert set(prs.columns) == {
        "id",
        "author",
        "changed_files",
        "comments",
        "closed",
        "closed_at",
        "created_at",
        "merged",
        "merged_at",
        "state",
        "updated_at",
        "total_comments_count",
        "reviews",
    }


def test_get_issues_empty_repo(mock_github):  # noqa: ARG001
    issues = get_issues("alan-turing-institute", "empty-repo")
    assert len(issues) == 0
    assert set(issues.columns) == {
        "title",
        "body",
        "author",
        "created_at",
        "closed_at",
        "comments",
        "labels",
    }
