import math

import pandas as pd

from github_analyser.utils import query_with_pagination


def _get_commits_query(org_name: str, repo_name: str) -> str:
    return f"""
    query ($afterCursor: String) {{
        repository(owner: "{org_name}", name: "{repo_name}") {{
            defaultBranchRef {{
                target {{
                    ... on Commit {{
                        history(first: 10, after: $afterCursor) {{
                            edges {{
                                node {{
                                    messageHeadline
                                    author {{
                                        name
                                        date
                                    }}
                                    additions
                                    deletions
                                }}
                            }}
                            pageInfo {{
                                endCursor
                                hasNextPage
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    """


def get_commits(
    org_name: str,
    repo_name: str,
    total_commits_to_fetch=20,
    save: bool | str = False,
) -> pd.DataFrame:
    """Fetch info about commits from a GitHub repository.

    Args:
        org_name: The owner of the repository.
        repo_name: The name of the repository.
        total_commits_to_fetch: The total number of commits to fetch.
        save (bool | str, optional): If True, save the data to "data/commits.csv" or
        specify a path. Defaults to False.

    Returns:
        A pandas DataFrame with the following columns:
            - message: The commit message.
            - additions: The number of additions in the commit.
            - deletions: The number of deletions in the commit.
            - author: The author of the commit.
            - date: The date of the commit.
    """
    query = _get_commits_query(org_name, repo_name)
    max_pages_to_fetch = math.ceil(total_commits_to_fetch / 10)

    responses = query_with_pagination(
        query,
        ["data", "repository", "defaultBranchRef", "target", "history"],
        "afterCursor",
        max_pages=max_pages_to_fetch,
    )

    nodes = []
    for response in responses:
        edges = response["data"]["repository"]["defaultBranchRef"]["target"]["history"][
            "edges"
        ]
        nodes.extend(edge["node"] for edge in edges)
        if len(nodes) >= total_commits_to_fetch:
            break

    nodes = nodes[:total_commits_to_fetch]

    df = pd.json_normalize(nodes, sep="_")
    df.rename(
        columns={
            "messageHeadline": "message",
            "author_name": "author",
            "author_date": "date",
        },
        inplace=True,
    )

    if save:
        if save is True:
            save = f"data/{repo_name}/commits.csv"
        df.to_csv(save, index=False)

    return df
