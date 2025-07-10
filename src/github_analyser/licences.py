from __future__ import annotations

import pathlib

import pandas as pd

from github_analyser.utils import camel_to_snake, request_github_graphql


def _get_licence_query(org_name: str, repo_name: str) -> str:
    return f"""
    query {{
        repository(owner: "{org_name}", name: "{repo_name}") {{
            id
            url
            licenseInfo {{
                id
                name
                spdxId
            }}
        }}
    }}
    """


def get_licence(
    org_name: str,
    repo_name: str,
) -> pd.DataFrame:
    """Fetch info about licences from a GitHub repository.

    Args:
        org_name: The owner of the repository.
        repo_name: The name of the repository.

    Returns:
        A pandas Series containing the repository ID, licence name, and SPDX ID.
    """
    query = _get_licence_query(org_name, repo_name)

    response = request_github_graphql({"query": query})
    # extract repo id from the first response
    repo_id = None
    if response:
        repo_id = response["data"]["repository"]["id"]
        repo_url = response["data"]["repository"]["url"]

    licence_info = response["data"]["repository"]["licenseInfo"]

    if licence_info is None:
        return pd.Series(
            {
                "repo_name": repo_name,
                "repo_url": repo_url,
                "repo_id": repo_id,
                "name": None,
                "spdx_id": None,
            }
        )

    name = licence_info.get("name", "")
    spdx_id = licence_info.get("spdxId", "")
    return pd.Series(
        {
            "repo_name": repo_name,
            "repo_url": repo_url,
            "repo_id": repo_id,
            "name": name,
            "spdx_id": spdx_id,
        }
    )


def get_licences(
    org_name: str,
    repo_names: list[str],
    save: bool | str = False,
) -> pd.DataFrame:
    """Get information about licences for multiple repositories within an organization.

    Args:
        org_name: The owner of the repositories.
        repo_names: A list of repository names.
        save (bool | str, optional): If True, save the data to "data/licences.csv".
            If a string, save to that path. Defaults to False.

    Returns:
        A pandas DataFrame containing the repository IDs, licence names, and SPDX IDs.

    """
    if not isinstance(repo_names, list):
        msg = "`repo_names` must be a list of repository names."
        raise ValueError(msg)

    data = []
    for repo_name in repo_names:
        series = get_licence(org_name, repo_name)
        data.append(series)

    df = pd.DataFrame(data)
    df.rename(columns=camel_to_snake, inplace=True)

    if save:
        if save is True:
            if not pathlib.Path.exists("data"):
                pathlib.Path.mkdir("data")
            save = f"data/{repo_name}/licences.csv"
        df.to_csv(save, index=False)

    return df
