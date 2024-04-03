from functools import reduce

import pandas as pd

from github_analyser.utils import camel_to_snake, query_with_pagination


def _get_team_members_query(org_name: str, team_slug: str):
    return f"""
    query ($pagination_cursor: String) {{
      organization(login: "{org_name}") {{
        team(slug: "{team_slug}") {{
          members(first: 30, after: $pagination_cursor) {{
            pageInfo {{
              hasNextPage
              endCursor
            }}
            totalCount
            edges {{
              node {{
                login
              }}
            }}
          }}
        }}
      }}
    }}
    """


def get_team_members(org_name: str, team_slug: str, save: bool | str = False):
    """Get all members of a team within an organisation on GitHub.

    Args:
        org_name (str): The name of the organisation.
        team_slug (str): The slug of the team.
        save (bool | str, optional): If True, save the data to "data/org_teams.csv" or
        specify a path. Defaults to False.

    Returns:
        pandas Dataframe: One row per user, columns login.
    """
    pages = query_with_pagination(
        _get_team_members_query(org_name, team_slug),
        page_info_path=["data", "organization", "team", "members"],
    )
    edges = [
        reduce(
            lambda x, key: x[key],
            ["data", "organization", "team", "members", "edges"],
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
            save = "data/org_teams.csv"
        df.to_csv(save, index=False)

    return df
