# github-analyser

[![Actions Status][actions-badge]][actions-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

## Installation

```bash
python -m pip install github_analyser
```

From source:

```bash
git clone https://github.com/alan-turing-institute/github-analyser
cd github-analyser
python -m pip install .
```

## Usage

### Authentication

All functions require a GitHub personal access token with appropriate
permissions.

You will need to set it as an environment variable:

```bash
export GITHUB_TOKEN=your_token_here
```

### Functions

All functions return a pandas DataFrame and accept an optional `save` argument.

- Setting `save=True` will cause the data to be saved to `data/`
- Setting `save="path/to/file.csv"` will cause the data to be saved to the
  specified path.

**Org-level data:**

```python
from github_analyser.org_user_info import get_org_members, get_org_teams
from github_analyser.repos import get_repos

# list all repositories in an organisation
repos = get_repos("my-org")

# list all members of an organisation
members = get_org_members("my-org")

# list all teams in an organisation
teams = get_org_teams("my-org")
```

**Team and repo-level data:**

```python
from github_analyser.team_user_info import get_team_members
from github_analyser.repo_user_info import get_repo_collaborators
from github_analyser.repo_contributors import get_repo_contributors
from github_analyser.commits import get_commits
from github_analyser.issues import get_issues
from github_analyser.pull_requests import get_pull_requests
from github_analyser.licences import get_licences

# list members of a team (use the team slug, e.g. "my-team")
members = get_team_members("my-org", "my-team")

# list collaborators of a repository
collaborators = get_repo_collaborators("my-org", "my-repo")

# get contributor commit counts for a repository
contributors = get_repo_contributors("my-org", "my-repo")

# get commits from the default branch of a repository
commits = get_commits("my-org", "my-repo")

# get issues from a repository
issues = get_issues("my-org", "my-repo")

# get pull requests from a repository
prs = get_pull_requests("my-org", "my-repo")

# get licence information for one or more repositories
licences = get_licences("my-org", ["repo-one", "repo-two"])
```

**Saving results to CSV:**

```python
# save to the default path
repos = get_repos("my-org", save=True)

# save to a custom path
repos = get_repos("my-org", save="output/repos.csv")
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to contribute.

## License

Distributed under the terms of the [MIT license](LICENSE).

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/alan-turing-institute/github-analyser/workflows/CI/badge.svg
[actions-link]:             https://github.com/alan-turing-institute/github-analyser/actions
[pypi-link]:                https://pypi.org/project/github-analyser/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/github-analyser
[pypi-version]:             https://img.shields.io/pypi/v/github-analyser
<!-- prettier-ignore-end -->
