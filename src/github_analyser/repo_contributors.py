from __future__ import annotations

import pandas as pd

from github_analyser.utils import request_github_rest


def get_repo_contributors(
    org_name: str,
    repo_name: str,
    save: bool | str = False,
) -> pd.DataFrame:
    """Fetch info about contributors of a repository.

    Args:
        org_name: The owner of the repository.
        repo_name: The name of the repository.
        save (bool | str, optional): If True, save the data to "data/commits.csv" or
        specify a path. Defaults to False.

    Returns:
        A pandas DataFrame with the following columns:
            TODO
    """
    data = request_github_rest(
        "get", f"repos/{org_name}/{repo_name}/stats/contributors"
    )
    data = [{"login": x["author"]["login"], "commits": x["total"]} for x in data]
    df = pd.DataFrame(data)

    if save:
        if save is True:
            save = f"data/{repo_name}/repo_contributors.csv"
        df.to_csv(save, index=False)

    return df


if __name__ == "__main__":
    get_repo_contributors("alan-turing-institute", "github-analyser")
