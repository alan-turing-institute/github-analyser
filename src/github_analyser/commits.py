from __future__ import annotations

import math

import pandas as pd

from github_analyser.utils import camel_to_snake, query_with_pagination


def _get_commits_query(org_name: str, repo_name: str) -> str:
    return f"""
    query ($afterCursor: String) {{
        repository(owner: "{org_name}", name: "{repo_name}") {{
            id
            defaultBranchRef {{
                target {{
                    ... on Commit {{
                        history(first: 10, after: $afterCursor) {{
                            edges {{
                                node {{
                                    id
                                    oid
                                    messageHeadline
                                    author {{
                                        name
                                        date
                                    }}
                                    changedFiles
                                    additions
                                    deletions
                                    associatedPullRequests(first: 5) {{
                                        nodes {{
                                            id
                                        }}
                                    }}
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
    total_commits_to_fetch: int | None = None,
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

    if total_commits_to_fetch is not None:
        max_pages_to_fetch = math.ceil(total_commits_to_fetch / 10)
    else:
        max_pages_to_fetch = None

    responses = query_with_pagination(
        query,
        ["data", "repository", "defaultBranchRef", "target", "history"],
        "afterCursor",
        max_pages=max_pages_to_fetch,
    )

    # extract repo id from the first response
    repo_id = None
    if responses:
        repo_id = responses[0]["data"]["repository"]["id"]

    nodes = []
    for response in responses:
        edges = response["data"]["repository"]["defaultBranchRef"]["target"]["history"][
            "edges"
        ]
        nodes.extend(edge["node"] for edge in edges)
        if total_commits_to_fetch is not None and len(nodes) >= total_commits_to_fetch:
            break

    if total_commits_to_fetch is not None:
        nodes = nodes[:total_commits_to_fetch]

    df = pd.json_normalize(nodes, sep="_")
    df.rename(
        columns={
            "messageHeadline": "message",
            "author_name": "author",
            "author_date": "date",
            "oid": "hash",
            "associatedPullRequests_nodes": "pr_id",
        },
        inplace=True,
    )
    df.rename(columns=camel_to_snake, inplace=True)
    df["pr_id"] = df["pr_id"].apply(lambda x: x[0]["id"] if x else None)
    # add repo_id to the dataframe
    df["repo_id"] = repo_id

    if save:
        if save is True:
            save = f"data/{repo_name}/commits.csv"
        df.to_csv(save, index=False)

    return df
