import logging
from functools import reduce

import pandas as pd

from github_analyser.utils import query_with_pagination

MAX_COMMENTS = 100
MAX_LABELS = 10


def _issues_query(repo_name: str) -> str:
    return f"""
query ($pagination_cursor: String) {{
  repository(owner: "alan-turing-institute", name: "{repo_name}") {{
    issues(first: 100, after: $pagination_cursor, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
      pageInfo {{
        endCursor
        hasNextPage
      }}
      edges {{
        node {{
          title
          body
          createdAt
          closedAt
          author {{
            login
          }}
          comments(first: {MAX_COMMENTS}) {{
            totalCount
            edges {{
              node {{
                author {{
                  login
                }}
                createdAt
                body
              }}
            }}
          }}
          labels(first: {MAX_LABELS}) {{
            totalCount
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


def _author_login(node):
    author = node["author"]
    if author is None:
        return None
    return author["login"]


def get_issues(repo_name: str) -> pd.DataFrame:
    """Get all issues from a repository.

    Returns:
        pandas Dataframe: One row per issue.
    """
    query = _issues_query(repo_name)
    pages = query_with_pagination(
        query, page_info_path=["data", "repository", "issues"]
    )
    edges = [
        reduce(
            lambda x, key: x[key],
            ["data", "repository", "issues", "edges"],
            page,
        )
        for page in pages
    ]
    flattened_edges = sum(edges, [])
    nodes = [x["node"] for x in flattened_edges]
    for node in nodes:
        node["author"] = _author_login(node)

        if node["comments"]["totalCount"] > MAX_COMMENTS:
            logging.warning(
                "Issue %s has more than %d comments, some are left out",
                node["title"],
                MAX_COMMENTS,
            )
        node["comments"] = [
            _author_login(edge["node"]) for edge in node["comments"]["edges"]
        ]

        if node["labels"]["totalCount"] > MAX_LABELS:
            logging.warning(
                "Issue %s has more than %d labels, some are left out",
                node["title"],
                MAX_LABELS,
            )
        node["labels"] = [edge["node"]["name"] for edge in node["labels"]["edges"]]
    # TODO The columns all have a type of `object`, even though e.g. `createdAt` is a
    # date and `title` is a string.
    return pd.DataFrame(nodes)
