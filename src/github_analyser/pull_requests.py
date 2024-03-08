from __future__ import annotations

import pandas as pd

from github_analyser.utils import camel_to_snake, query_with_pagination


def _get_pull_requests_query(org_name: str, repo_name: str):
    """
    Retrieves pull requests data for a given repository.

    Args:
        org_name (str): The name of the organisation.
        repo_name (str): The name of the repository.

    Returns:
        str: The query string.
    """
    return f"""
        query ($pagination_cursor: String) {{
            repository(owner: "{org_name}", name: "{repo_name}") {{
                pullRequests(first: 10, after: $pagination_cursor) {{
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                    totalCount
                    edges {{
                        node {{
                            id
                            author {{
                                login
                            }}
                            changedFiles
                            comments(first:100) {{
                                edges {{
                                    node {{
                                        author {{
                                            login
                                        }}
                                    }}
                                }}
                            }}
                            closed
                            closedAt
                            createdAt
                            merged
                            mergedAt
                            state
                            updatedAt
                            totalCommentsCount
                            reviews(first: 10) {{
                                edges {{
                                    node {{
                                        author {{
                                            login
                                        }}
                                        state
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
    }}
    """


def _get_authors(edge):
    """
    Get the authors from nested dictionary.

    Args:
        edge (list): A list of edges.

    Returns:
        str: A string containing a comma separated list of the names of the authors.
        Deleted authors are represented by pd.NA.
    """
    authors = [i["node"]["author"].get("login", pd.NA) for i in edge]
    if len(authors) > 0:
        return (", ").join(authors)
    return ""


def get_pull_requests(org_name: str, repo_name: str, save: bool | str = False):
    """
    Retrieves pull requests data for a given repository and returns it as a pandas DataFrame.

    Args:
        org_name (str): The name of the organization.
        repo_name (str): The name of the repository.
        save (bool | str, optional): If True, save the data to
        "data/{repo_name}/pull_requests.csv" or specify a path. Defaults to False.

    Returns:
        pandas.DataFrame: The DataFrame containing pull requests data.
    """
    query = _get_pull_requests_query(org_name, repo_name)
    data = query_with_pagination(
        query,
        page_info_path=["data", "repository", "pullRequests"],
    )
    data_nodes = [
        edge["node"]
        for datum in data
        for edge in datum["data"]["repository"]["pullRequests"]["edges"]
    ]
    df = pd.json_normalize(data_nodes, sep="_")
    df["comments"] = df["comments_edges"].apply(_get_authors)
    df["reviews"] = df["reviews_edges"].apply(_get_authors)
    df.drop(columns=["comments_edges", "reviews_edges"], inplace=True)

    # rename columns to snake case
    df.rename(columns={"author_login": "author"}, inplace=True)
    df.rename(columns=camel_to_snake, inplace=True)

    if save:
        if save is True:
            save = f"data/{repo_name}/pull_requests.csv"
        df.to_csv(save, index=False)

    return df
