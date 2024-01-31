import pandas as pd

from github_analyser.utils import query_with_pagination


def get_pull_requests_data(repo_name):
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


def get_pull_requests_df(repo_name):
    data = get_pull_requests_data(repo_name=repo_name)
    data_nodes = [
        edge["node"]
        for datum in data
        for edge in datum["data"]["repository"]["pullRequests"]["edges"]
    ]
    df = pd.json_normalize(data_nodes)
    df["comments"] = df["comments.edges"].apply(get_authors)
    df["reviews"] = df["reviews.edges"].apply(get_authors)
    df.drop(columns=["comments.edges", "reviews.edges"], inplace=True)
    return df


def get_authors(edge):
    authors = [i["node"]["author"]["login"] for i in edge]
    if len(authors) > 0:
        return (", ").join(authors)
    return ""
