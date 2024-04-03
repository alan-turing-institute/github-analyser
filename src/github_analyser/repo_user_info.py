from functools import reduce

import pandas as pd

from github_analyser.utils import camel_to_snake, query_with_pagination


def _get_repo_collaborators(org_name: str, repo_name: str):
    """
    Retrieves collaborators for a given repository.

    Args:
        org_name (str): The name of the organisation.
        repo_name (str): The name of the repository.

    Returns:
        str: The query string.
    """
    return f"""
    query ($pagination_cursor: String) {{
      repository(owner: "{org_name}", name: "{repo_name}") {{
        collaborators(first: 10, after: $pagination_cursor) {{
          pageInfo {{
            endCursor
            hasNextPage
          }}
          edges {{
            node {{
              login
            }}
          }}
        }}
      }}
    }}
    """


def get_repo_collaborators(org_name: str, repo_name: str, save: bool | str = False):
    """
    Retrieves collaborators for a given repository.

    Args:
        org_name (str): The name of the organization.
        repo_name (str): The name of the repository.
        save (bool | str, optional): If True, save the data to
        "data/{repo_name}/collaborators.csv" or specify a path. Defaults to False.

    Returns:
        pandas.DataFrame: The DataFrame containing the collaborators.
    """
    query = _get_repo_collaborators(org_name, repo_name)
    data = query_with_pagination(
        query,
        page_info_path=["data", "repository", "collaborators"],
    )
    edges = [
        reduce(
            lambda x, key: x[key],
            ["data", "repository", "collaborators", "edges"],
            page,
        )
        for page in data
    ]
    flattened_edges = sum(edges, [])
    df = pd.json_normalize(flattened_edges)

    # rename columns to snake case
    df.rename(columns={"node.login": "login"}, inplace=True)
    df.rename(columns=camel_to_snake, inplace=True)

    if save:
        if save is True:
            save = f"data/{repo_name}/collaborators.csv"
        df.to_csv(save, index=False)

    return df
