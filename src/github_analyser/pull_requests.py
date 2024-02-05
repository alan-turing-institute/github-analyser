import pandas as pd

from github_analyser.utils import camel_to_snake, query_with_pagination


def get_pull_requests_data(repo_name: str):
    """
    Retrieves pull requests data for a given repository.

    Args:
        repo_name (str): The name of the repository.

    Returns:
        dict: The pull requests data in json format.

    """
    query = """
        query ($issues_end_cursor: String) {
            repository(owner: "alan-turing-institute", name: "%s") {
                pullRequests(first: 10, after: $issues_end_cursor, states: OPEN) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    totalCount
                    edges {
                        node {
                            id
                            author {
                                login
                            }
                            changedFiles
                            comments(first:100) {
                                edges {
                                    node {
                                        author {
                                            login
                                        }
                                    }
                                }
                            }
                            closed
                            closedAt
                            createdAt
                            lastEditedAt
                            merged
                            mergedAt
                            mergedBy {
                                login
                            }
                            state
                            updatedAt
                            totalCommentsCount
                            reviews(first: 10) {
                                edges {
                                    node {
                                        author {
                                            login
                                        }
                                        state
                                    }
                                }
                            }
                        }
                    }
                }
            }
    }
    """ % (
        repo_name
    )

    return query_with_pagination(query, ["data", "repository", "pullRequests"])


def get_pull_requests_df(repo_name: str, save: bool = False):
    """
    Retrieves pull requests data for a given repository and returns it as a pandas DataFrame.

    Args:
        repo_name (str): The name of the repository.
        save (bool): Whether to save the DataFrame as a csv file.

    Returns:
        pandas.DataFrame: The DataFrame containing pull requests data.
    """
    data = get_pull_requests_data(repo_name=repo_name)
    data_nodes = [
        edge["node"]
        for datum in data
        for edge in datum["data"]["repository"]["pullRequests"]["edges"]
    ]
    df = pd.json_normalize(data_nodes, sep="_")
    df["comments"] = df["comments_edges"].apply(get_authors)
    df["reviews"] = df["reviews_edges"].apply(get_authors)
    df.drop(columns=["comments_edges", "reviews_edges"], inplace=True)

    # rename columns to snake case
    df.rename(columns=camel_to_snake, inplace=True)

    if save:
        df.to_csv(f"data/{repo_name}/pull_requests.csv", index=False)

    return df


def get_authors(edge):
    """
    Get the authors from nested dictionary.

    Args:
        edge (list): A list of edges.

    Returns:
        str: A string containing a comma separated list of the names of the authors.
    """
    authors = [
        i["node"]["author"].get("login", ":ghost:") for i in edge
    ]  # allow for ghosts (how can i make this the emoji?)
    if len(authors) > 0:
        return (", ").join(authors)
    return ""
