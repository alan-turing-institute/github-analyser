from functools import reduce

import pandas as pd

from github_analyser.utils import camel_to_snake, query_with_pagination

repos_query = """
query ($pagination_cursor: String) {
  organization(login: "alan-turing-institute") {
    repositories(first: 100, after: $pagination_cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo {
        endCursor
        hasNextPage
      }
      edges {
        node {
          id
          name
          updatedAt
          url
        }
      }
    }
  }
}
"""


def get_repos():
    """Get all repositories from the Alan Turing Institute organisation on GitHub.

    Returns:
        pandas Dataframe: One row per repo, columns repository name, id, url and last
        updated date.
    """
    pages = query_with_pagination(
        repos_query, page_info_path=["data", "organization", "repositories"]
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

    df = pd.DataFrame(nodes)
    df.rename(columns=camel_to_snake, inplace=True)

    return df
