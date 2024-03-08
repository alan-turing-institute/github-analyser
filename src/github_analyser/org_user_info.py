from functools import reduce

import pandas as pd

from github_analyser.utils import camel_to_snake, query_with_pagination


def _get_org_members_query(org_name: str):
    return f"""
    query ($pagination_cursor: String) {{
      organization(login: "{org_name}") {{
        membersWithRole(first: 30, after: $pagination_cursor) {{
          pageInfo {{
            hasNextPage
            endCursor
          }}
          totalCount
          edges {{
            role
            node {{
              login
            }}
          }}
        }}
      }}
    }}
    """


def _get_org_teams_query(org_name: str):
    return f"""
    query ($pagination_cursor: String) {{
      organization(login: "{org_name}") {{
        teams(first: 30, after: $pagination_cursor) {{
          pageInfo {{
            hasNextPage
            endCursor
          }}
          totalCount
          edges {{
            node {{
              name
              slug
            }}
          }}
        }}
      }}
    }}
    """


def get_org_members(org_name: str, save: bool | str = False):
    """Get all members from an organisation on GitHub.

    Args:
        org_name (str): The name of the organisation.
        save (bool | str, optional): If True, save the data to "data/org_members.csv" or
        specify a path. Defaults to False.

    Returns:
        pandas Dataframe: One row per login, columns login and role.
    """
    pages = query_with_pagination(
        _get_org_members_query(org_name),
        page_info_path=["data", "organization", "membersWithRole"],
    )
    edges = [
        reduce(
            lambda x, key: x[key],
            ["data", "organization", "membersWithRole", "edges"],
            page,
        )
        for page in pages
    ]
    flattened_edges = sum(edges, [])
    df = pd.json_normalize(flattened_edges)
    df.rename(columns={"node.login": "login"}, inplace=True)
    df.rename(columns=camel_to_snake, inplace=True)

    if save:
        if save is True:
            save = "data/org_members.csv"
        df.to_csv(save, index=False)

    return df


def get_org_teams(org_name: str, save: bool | str = False):
    """Get all teams from an organisation on GitHub.

    Args:
        org_name (str): The name of the organisation.
        save (bool | str, optional): If True, save the data to "data/org_teams.csv" or
        specify a path. Defaults to False.

    Returns:
        pandas Dataframe: One row per team, columns name.
    """
    pages = query_with_pagination(
        _get_org_teams_query(org_name),
        page_info_path=["data", "organization", "teams"],
    )
    edges = [
        reduce(
            lambda x, key: x[key],
            ["data", "organization", "teams", "edges"],
            page,
        )
        for page in pages
    ]
    flattened_edges = sum(edges, [])
    df = pd.json_normalize(flattened_edges)
    df.rename(columns={"node.name": "name", "node.slug": "slug"}, inplace=True)
    df.rename(columns=camel_to_snake, inplace=True)

    if save:
        if save is True:
            save = "data/org_teams.csv"
        df.to_csv(save, index=False)

    return df
