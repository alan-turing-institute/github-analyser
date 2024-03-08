from functools import reduce

import pandas as pd

from github_analyser.utils import camel_to_snake, query_with_pagination


def _get_repos_query(org_name: str):
    return f"""
    query ($pagination_cursor: String) {{
      organization(login: "{org_name}") {{
        repositories(first: 100, after: $pagination_cursor, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
          pageInfo {{
            endCursor
            hasNextPage
          }}
          edges {{
            node {{
              id
              name
              updatedAt
              url
              languages(first: 10) {{
                edges {{
                  node {{
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """


def get_repos(org_name: str, save: bool | str = False):
    """Get all repositories from the Alan Turing Institute organisation on GitHub.

    Args:
        org_name (str): The name of the organisation.
        save (bool | str, optional): If True, save the data to "data/repos.csv" or
        specify a path. Defaults to False.

    Returns:
        pandas Dataframe: One row per repo, columns repository name, id, url and last
        updated date.
    """
    pages = query_with_pagination(
        _get_repos_query(org_name),
        page_info_path=["data", "organization", "repositories"],
    )
    edges = [
        reduce(
            lambda x, key: x[key],
            ["data", "organization", "repositories", "edges"],
            page,
        )
        for page in pages
    ]
    flattened_edges = sum(edges, [])
    nodes = [x["node"] for x in flattened_edges]
    for node in nodes:
        node["languages"] = [x["node"]["name"] for x in node["languages"]["edges"]]
    df = pd.DataFrame(nodes)
    df.rename(columns=camel_to_snake, inplace=True)

    if save:
        if save is True:
            save = "data/repos.csv"
        df.to_csv(save, index=False)

    return df
